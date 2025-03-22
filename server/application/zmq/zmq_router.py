import zmq
import json
import time
import subprocess
import requests
from application.services.portfolio_service import PortfolioService
from application.container import container

# Cache for predictions
prediction_cache = {}
cache_expiry_seconds = 20

# Connection tracking
clients = {}  # {identity: last_seen_time}
identity_to_portfolio = {}  # {identity: portfolio_id}
HEARTBEAT_TIMEOUT = 5  # Seconds before marking a client as disconnected

# ZeroMQ context and sockets
context = zmq.Context()
socket = context.socket(zmq.ROUTER)  # Handles client messages
socket_publisher = context.socket(zmq.PUB)  # Broadcast updates

socket.bind("tcp://*:5557")  # Router socket
socket_publisher.bind("tcp://*:5555")  # Publisher socket

poller = zmq.Poller()  # Poller for non-blocking mode
poller.register(socket, zmq.POLLIN)

print("ZeroMQ server is running...")

while True:
  try:
    # 🔍 **Check if a message is available (Non-Blocking)**
    events = dict(poller.poll(timeout=100))  # 100ms timeout

    if socket in events:
      identity, message = socket.recv_multipart()
      message_str = message.decode("utf-8", "ignore")

      print(f"Received from {identity.hex()}: {message_str}")

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

        if data:
          model_id = data.get("model_id")
          is_expert = bool(data.get("is_expert"))  
          portfolio_id = data.get("portfolio_id")

          identity_to_portfolio[identity] = portfolio_id

          current_time = time.time()

          expired_keys = [key for key, (_, timestamp) in prediction_cache.items() if current_time - timestamp > cache_expiry_seconds]
          for key in expired_keys:
            del prediction_cache[key]

          if model_id in prediction_cache and current_time - prediction_cache[model_id][1] < cache_expiry_seconds:
            response = prediction_cache[model_id][0]
          else:
            command = ["python", "-m", f"models.{model_id}.publisher", model_id]
            result = subprocess.run(command, capture_output=True, text=True)
            response = result.stdout.strip().encode() if result.returncode == 0 else b""
            prediction_cache[model_id] = (response, current_time)

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

      # ✅ **Send response back to client**
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
