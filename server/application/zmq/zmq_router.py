import zmq
import json
import time
import subprocess

prediction_cache = {}

context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind("tcp://*:5557")

print("ZeroMQ server is running...")

while True:
  try:
    # ROUTER socket receives [identity] + [message]
    identity, message = socket.recv_multipart()
    message_str = message.decode(errors="ignore")  # Ignore invalid UTF-8 errors

    print(f"Received from {identity.hex()}: {message_str}")

    # Process request
    response = None  
    if "signal_request" in message_str:
      data = json.loads(message_str)
      model_id = data.get("model_id")
      
      if model_id in prediction_cache:
        response = prediction_cache[model_id]
      else:
        command = f"python -m models.{model_id}.publisher"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        response = result.stdout.strip() if result.returncode == 0 else "ERROR"
        prediction_cache[model_id] = response  # Store in cache
    
    elif "init" in message_str:
      response = "initialized"
    elif "end" in message_str:
      response = "terminated" 

    if response:
      # Correctly send response **immediately** with identity
      socket.send_multipart([identity, response.encode("utf-8")])
      print(f"Sent to {identity.hex()}: {response}")

    time.sleep(0.001)  # Prevent CPU overuse

  except KeyboardInterrupt:
    print("Server shutting down...")
    break
