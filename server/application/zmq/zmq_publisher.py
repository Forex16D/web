import zmq
import json
import time
import random
from datetime import datetime, timezone

# Initialize ZeroMQ context
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")  # Publishing on TCP port 5555

print("ZeroMQ publisher is running...")

# List of possible trade symbols
symbols = ["EURUSD"]

while True:
  try:
    # Simulating a model prediction
    model_id = "20dcda30-486c-42e1-a8d0-908be1a18f86"  # Unique expert ID
    signal = random.choice(["BUY", "SELL"])  # Trading signal (no HOLD)
    symbol = random.choice(symbols)  # Random trading pair
    price = round(random.uniform(1.1000, 1.5000), 5)  # Simulated price
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

    # Construct message payload
    message = {
      "model_id": model_id,
      "signal": signal,
      "symbol": symbol,
      "price": price,
      "timestamp": timestamp
    }

    # Use multipart send: First part = `model_id`, Second part = JSON message
    socket.send_multipart([model_id.encode(), json.dumps(message).encode()])
    print(f"Published: {message}")

    time.sleep(5)  # Simulate delay before sending the next prediction

  except KeyboardInterrupt:
    print("Publisher shutting down...")
    break
