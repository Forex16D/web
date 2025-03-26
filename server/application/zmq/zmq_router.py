import zmq
import json
import time
import subprocess
import requests
from application.services.portfolio_service import PortfolioService
from application.container import container
from concurrent.futures import ThreadPoolExecutor  # Import the ThreadPoolExecutor
from application.container import container

# Cache for predictions
prediction_cache = {}
cache_expiry_seconds = 5

# Connection tracking
clients = {}  # {identity: last_seen_time}
identity_to_portfolio = {}  # {identity: portfolio_id}
HEARTBEAT_TIMEOUT = 60  # Seconds before marking a client as disconnected

# ZeroMQ context and sockets
context = zmq.Context()
socket = context.socket(zmq.ROUTER)  # Handles client messages
socket_publisher = context.socket(zmq.PUB)  # Broadcast updates

socket.bind("tcp://*:5557")  # Router socket
socket_publisher.bind("tcp://*:5555")  # Publisher socket

poller = zmq.Poller()  # Poller for non-blocking mode
poller.register(socket, zmq.POLLIN)

# Thread pool to handle background prediction
executor = ThreadPoolExecutor(max_workers=3)  # Max 3 concurrent threads for predictions

print("ZeroMQ server is running...")

def run_prediction_in_background(model_id, data, response_callback):
    data_str = json.dumps(data)
    command = ["python", "-m", f"models.{model_id}.publisher", data_str]
    result = subprocess.run(command, capture_output=True, text=True)
    response = result.stdout.strip().encode() if result.returncode == 0 else b""
    response_callback(response)

while True:
  try:
    # 🔍 **Check if a message is available (Non-Blocking)**
    events = dict(poller.poll(timeout=100))  # 100ms timeout

    if socket in events:
      identity, message = socket.recv_multipart()
      message_str = message.decode("utf-8", "ignore")
      
      if not message_str.strip():
        continue

      print(f"Received from {identity.hex()}")
      response = None
      clients[identity] = time.time()  # Update last seen time

      # 🟢 **Process Signal Requests**
      if "signal_request" in message_str:
        try:
          data = json.loads(message_str)
          if isinstance(data, str):
            data = json.loads(data)
        except json.JSONDecodeError as e:
          print(f"JSON Decode Error: {e} | Raw: {message_str}")
          data = None

        is_expert = False
        is_banned = container.user_service.check_ban_status_from_portfolio(data.get("portfolio_id"))
        if is_banned:
          response = b"User is banned!"

        elif data:
          model_id = data.get("model_id")
          is_expert = bool(data.get("is_expert"))  
          portfolio_id = data.get("portfolio_id")
          market_data = data.get("market_data")
          identity_to_portfolio[identity] = portfolio_id  # Store mapping

          current_time = time.time()

          # ✅ **Remove expired cache**
          expired_keys = [key for key, (_, timestamp) in prediction_cache.items() if current_time - timestamp > cache_expiry_seconds]
          for key in expired_keys:
            del prediction_cache[key]

          # ✅ **Use cached response if available**
          if model_id in prediction_cache and current_time - prediction_cache[model_id][1] < cache_expiry_seconds:
            response = prediction_cache[model_id][0]
          else:
            # Run prediction in a separate thread
            def handle_prediction_result(response):
                # When prediction is done, store it in cache and send the response
                prediction_cache[model_id] = (response, current_time)
                socket.send_multipart([identity, response])
                print(f"Sent to {identity.hex()}: {response}")
                # 🟠 **Publish signals if expert**
                if is_expert:
                    socket_publisher.send_multipart([model_id.encode(), response])
                    print(f"Published: {response}")
            
            # Submit to thread pool
            future = executor.submit(run_prediction_in_background, model_id, market_data, handle_prediction_result)

      # 🔵 **Handle Client Initialization**
      elif "init" in message_str:
        portfolio_id = message_str.split(" ")[-1]
        PortfolioService.update_connection_status(container.db_pool, portfolio_id, True)
        identity_to_portfolio[identity] = portfolio_id  # Store identity mapping
        response = b"Connection established..."

      # 🟡 **Process Orders**
      elif "order" in message_str:
        try:
          data = json.loads(message_str)
          if isinstance(data, str):
            data = json.loads(data)
        except json.JSONDecodeError as e:
          print(f"JSON Decode Error: {e} | Raw: {message_str}")
          data = None

        if data:
          token = data.pop("token", None)
          headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
          requests.post("http://localhost:5000/v1/mt/order", json=data, headers=headers)

      # 🔴 **Handle Client Disconnection**
      elif "end" in message_str:
        portfolio_id = message_str.split(" ")[-1]
        PortfolioService.update_connection_status(container.db_pool, portfolio_id, False)
        response = b"Closing connection..."
        identity_to_portfolio.pop(identity, None)  # Remove mapping

      # 💓 **Handle Heartbeats**
      elif "heartbeat" in message_str:
        print(f"Heartbeat received from {identity.hex()}")

      # ✅ **Send response back to client** (This is done once prediction is complete)
      if response:
        socket.send_multipart([identity, response])
        print(f"Sent to {identity.hex()}: {response}")

        # 🟠 **Publish signals if expert**
        if "signal_request" in message_str and is_expert:
          socket_publisher.send_multipart([model_id.encode(), response])
          print(f"Published: {response}")

    # 🔍 **Detect Disconnected Clients**
    now = time.time()
    disconnected_clients = [client for client, last_seen in clients.items() if now - last_seen > HEARTBEAT_TIMEOUT]

    for client in disconnected_clients:
      portfolio_id = identity_to_portfolio.get(client)
      if portfolio_id:
        print(f"Client {client.hex()} (Portfolio: {portfolio_id}) disconnected!")
        PortfolioService.update_connection_status(container.db_pool, portfolio_id, False)
        del identity_to_portfolio[client]  # Remove mapping
      del clients[client]  # Remove from active list

    time.sleep(0.001)  # Prevent CPU overuse

  except KeyboardInterrupt:
    print("Server shutting down...")
    break
