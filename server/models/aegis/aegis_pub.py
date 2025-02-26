import zmq
import time
import numpy as np
from stable_baselines3 import PPO
import json
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import sys

mode = sys.argv[1] if len(sys.argv) > 1 else "backtest"
assert mode in ["backtest", "deploy"], "Invalid mode. Use 'backtest' or 'deploy'."

context = zmq.Context()

if mode == "backtest":
  socket_recv = context.socket(zmq.REP)
  socket_recv.bind("tcp://127.0.0.1:5557")
  socket_send = None
else:
  socket_recv = context.socket(zmq.PULL)
  socket_recv.bind("tcp://127.0.0.1:5557")
  socket_send = context.socket(zmq.PUB)
  socket_send.bind("tcp://127.0.0.1:5555")

model_path = "./server/models/output/ppo_trading_model.zip"
model = PPO.load(model_path)

def evaluate_with_model(json_str):
  try:
    data_list = json.loads(json_str)
    df = pd.DataFrame(data_list)

    df.drop(columns=['time'], errors='ignore', inplace=True)
    df.rename(columns={"volumn": "tick_volume"}, inplace=True)

    numeric_cols = ['open', 'high', 'low','close']
    df[numeric_cols] = df[numeric_cols].astype(float)

    if len(df) < 109:
      print(f"Not enough data. Received only {len(df)} rows.")
      return "ERROR"

    df['EMA_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
    df['EMA_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['MACD'] = MACD(df['close']).macd()
    df['RSI'] = RSIIndicator(df['close']).rsi()
    bb = BollingerBands(df['close'], window=20)
    df['BB_Upper'] = bb.bollinger_hband()
    df['BB_Lower'] = bb.bollinger_lband()

    df = df.dropna()

    if len(df) < 60:
      print(f"Invalid data shape after indicators: {df.shape}. Expected (60, 11).")
      return "ERROR"

    df = df.tail(60)

    action_signal, _ = model.predict(df.values, deterministic=True)
    print(f"Predicted action signal: {action_signal}")

    action_signal = int(action_signal)
    action_map = {0: "hold", 1: "buy", 2: "sell", 3: "close_buy", 4: "close_sell"}
    return action_map.get(action_signal, "ERROR")

  except Exception as e:
    print(f"Error in evaluate_with_model: {e}")
    return "ERROR"

print(f"Python server running in '{mode}' mode... Press Ctrl+C to stop.")

try:
  while True:
    try:
      message = socket_recv.recv_string(flags=zmq.NOBLOCK)
      print(f"Received message. Length: {len(message)}")

      if message == "init":
        socket_recv.send_string("ACK")
        continue

      if mode == "backtest":
        try:
          ohlc_data = json.loads(message)
          if len(ohlc_data) != 109:
            print("Invalid number of rows. Expected 109 rows.")
            socket_recv.send_string("ERROR")
            continue

          signal = evaluate_with_model(json.dumps(ohlc_data))
        except json.JSONDecodeError:
          print("Invalid JSON format. Skipping...")
          signal = "ERROR"
        except KeyError as e:
          print(f"Missing key in data: {e}")
          signal = "ERROR"
        except Exception as e:
          print(f"Error processing data: {e}")
          signal = "ERROR"

        print(f"Sending signal: {signal}")
        socket_recv.send_string(signal)

      else:  # Deployment mode
        signal = evaluate_with_model(message)
        print(f"Publishing signal: {signal}")
        socket_send.send_string(signal)

    except zmq.error.Again:
      time.sleep(0.1)

except KeyboardInterrupt:
  print("\nServer interrupted. Closing...")

finally:
  print("Cleaning up ZeroMQ...")
  socket_recv.close()
  if socket_send:
    socket_send.close()
  context.term()
  print("Server shut down gracefully.")
