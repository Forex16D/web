import zmq
import json
import time
import subprocess
import requests

# Cache with timestamps
prediction_cache = {}
cache_expiry_seconds = 20

context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket_publisher = context.socket(zmq.PUB)

socket.bind("tcp://*:5557")
socket_publisher.bind("tcp://*:5555")

print("ZeroMQ server is running...")

while True:
  try:
    # ROUTER socket receives [identity] + [message]
    identity, message = socket.recv_multipart()
    message_str = message.decode("utf-8", "ignore")  # Keep as a string

    print(f"Received from {identity.hex()}: {message_str}")

    # Process request
    response = None

    if "signal_request" in message_str:
      try:
        data = json.loads(message_str)  # First attempt
        if isinstance(data, str):
          data = json.loads(data)
      except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw message received: {message_str}")
        data = None

      if data:
        model_id = data.get("model_id")
        is_expert = data.get("is_expert")
        portfolio_id = data.get("portfolio_id")
        current_time = time.time()

        # Clean up expired cache entries
        expired_keys = [key for key, (_, timestamp) in prediction_cache.items() if current_time - timestamp > cache_expiry_seconds]
        for key in expired_keys:
          del prediction_cache[key]

        if model_id in prediction_cache and current_time - prediction_cache[model_id][1] < cache_expiry_seconds:
          response = prediction_cache[model_id][0]  # Return cached response
        else:
          # Securely run the subprocess
          
          command = ["python", "-m", f"models.{model_id}.publisher", model_id]
          result = subprocess.run(command, capture_output=True, text=True)
          response = result.stdout.strip().encode() if result.returncode == 0 else ""
          prediction_cache[model_id] = (response, current_time)  # Store response with timestamp

    elif "init" in message_str:
      response = b"Server is running..."

    elif "order" in message_str:
      try:
        data = json.loads(message_str)  # First attempt
        if isinstance(data, str):
          data = json.loads(data)
      except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw message received: {message_str}")
        data = None

      requests.post("http://localhost:5000/v1/mt/order", json=data)

    if response:
      # Correctly send response **immediately** with identity
      socket.send_multipart([identity, response])
      print(f"Sent to {identity.hex()}: {response}")
      
      if is_expert:
        socket_publisher.send_multipart([model_id.encode(), response])
        print(f"Published: {response}")
    time.sleep(0.001)  # Prevent CPU overuse

  except KeyboardInterrupt:
    print("Server shutting down...")
    break
