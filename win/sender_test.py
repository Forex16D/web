import zmq
import json
import time

# ZeroMQ setup
context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind("tcp://127.0.0.1:5557")


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
      response = "buy"  
    elif "init" in message_str:
      response = "initialized"
    elif "end" in message_str:
      response = "terminated"

    if response:
      # Correctly send response **immediately** with identity
      socket.send_multipart([identity, "buy".encode("utf-8")])
      print(f"Sent to {identity.hex()}: {response}")

    time.sleep(0.001)  # Prevent CPU overuse

  except KeyboardInterrupt:
    print("Server shutting down...")
    break
