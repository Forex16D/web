import zmq
import numpy as np
from stable_baselines3 import PPO
import json
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:5557")

model_path = "./server/models/output/ppo_trading_model.zip"
model = PPO.load(model_path)

def evaluate_with_model(json_str):
  try:
    data_list = json.loads(json_str)
    df = pd.DataFrame(data_list)

    df.drop(columns=['time'], errors='ignore', inplace=True)
    df = df.drop(columns=['open', 'high', 'low', 'volume'], errors='ignore')

    numeric_cols = ['close']
    df[numeric_cols] = df[numeric_cols].astype(float)
    if len(df) < 120:
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
      print(f"Invalid data shape after indicators: {df.shape}. Expected (60, 7).")
      return "ERROR"

    df = df.tail(60)

    action_signal, _ = model.predict(df.values, deterministic=True)
    print(f"Predicted action signal: {action_signal}")

    action_signal = int(action_signal)  # Ensure it's an integer
    action_map = {0: "hold", 1: "buy", 2: "sell"}
    return action_map.get(action_signal, "ERROR")


  except Exception as e:
    print(f"Error in evaluate_with_model: {e}")
    return "ERROR"


print("Python server with ML model is ready... Press Ctrl+C to stop.")

try:
  while True:
    message = socket.recv_string()
    print(f"Received message. Length: {len(message)}")

    try:
      ohlc_data = json.loads(message)

      if len(ohlc_data) != 120:
        print("Invalid number of rows. Expected 100 rows.")
        socket.send_string("ERROR")
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
    socket.send_string(signal)

except KeyboardInterrupt:
  print("\nServer interrupted. Closing...")

finally:
  print("Cleaning up ZeroMQ...")
  socket.close()
  context.term()
  print("Server shut down gracefully.")
