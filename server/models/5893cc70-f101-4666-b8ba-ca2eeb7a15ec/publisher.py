from application.helpers.server_log_helper import ServerLogHelper
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from stable_baselines3 import PPO
import zmq
import time
import numpy as np
import json
import pandas as pd
from pathlib import Path
import sys
 
mode = sys.argv[1] if len(sys.argv) > 1 else "backtest"
assert mode in ["backtest", "deploy"], "Invalid mode. Use 'backtest' or 'deploy'."

context = zmq.Context()

if mode == "backtest":
  socket_recv = context.socket(zmq.REP)
  socket_recv.bind("tcp://*:5557")
  socket_send = None
else:
  socket_recv = context.socket(zmq.PULL)
  socket_recv.bind("tcp://*:5557")
  socket_send = context.socket(zmq.REP)
  socket_send.connect("tcp://*:5555")

model_path = Path(__file__).parent / "model"
model = PPO.load(model_path)

def close_connection():
  ServerLogHelper.log("Cleaning up ZeroMQ...")
  socket_recv.close()
  if socket_send:
    socket_send.close()
  context.term()
  context.term()
  ServerLogHelper.log("Server shut down gracefully.")

def evaluate_with_model(json_str):
  try:
    data_list = json.loads(json_str)
    df = pd.DataFrame(data_list)

    df.drop(columns=['time'], errors='ignore', inplace=True)
    df.rename(columns={"volumn": "tick_volume"}, inplace=True)

    numeric_cols = ['open', 'high', 'low','close']
    df[numeric_cols] = df[numeric_cols].astype(float)

    if len(df) < 109:
      ServerLogHelper.log(f"Not enough data. Received only {len(df)} rows.")
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
      ServerLogHelper.log(f"Invalid data shape after indicators: {df.shape}. Expected (60, 11).")
      return "ERROR"

    df = df.tail(60)

    action_signal, _ = model.predict(df.values, deterministic=True)
    ServerLogHelper.log(f"Predicted action signal: {action_signal}")

    action_signal = int(action_signal)
    action_map = {0: "hold", 1: "buy", 2: "sell", 3: "close_buy", 4: "close_sell"}
    return action_map.get(action_signal, "ERROR")

  except Exception as e:
    ServerLogHelper.log(f"Error in evaluate_with_model: {e}")
    return "ERROR"

ServerLogHelper.log(f"Python server running in '{mode}' mode... Press Ctrl+C to stop.")

try:
  while True:
    try:
      message = socket_recv.recv_string(flags=zmq.NOBLOCK)
      ServerLogHelper.log(f"Received message. Length: {len(message)}")

      if message == "init":
        socket_recv.send_string("ACK")
        continue
        
      if mode == "backtest":
        if message == "end":
          ServerLogHelper.log("End of backtest.")
          socket_recv.send_string("ACK")
          break

        try:
          ohlc_data = json.loads(message)
          if len(ohlc_data) != 109:
            ServerLogHelper.log("Invalid number of rows. Expected 109 rows.")
            socket_recv.send_string("ERROR")
            continue

          signal = evaluate_with_model(json.dumps(ohlc_data))
        except json.JSONDecodeError:
          ServerLogHelper.log("Invalid JSON format. Skipping...")
          signal = "ERROR"
        except KeyError as e:
          ServerLogHelper.log(f"Missing key in data: {e}")
          signal = "ERROR"
        except Exception as e:
          ServerLogHelper.log(f"Error processing data: {e}")
          signal = "ERROR"

        ServerLogHelper.log(f"Sending signal: {signal}")
        socket_recv.send_string(signal)

      else:  # Deployment mode
        signal = evaluate_with_model(message)
        ServerLogHelper.log(f"Sending signal: {signal}")
        socket_send.send_string(signal)

    except zmq.error.Again:
      time.sleep(0.1)

except KeyboardInterrupt:
  ServerLogHelper.log("\nServer interrupted. Closing...")

finally:
  close_connection()
