from application.helpers.server_log_helper import ServerLogHelper
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from stable_baselines3 import PPO
import json
import pandas as pd
import sys
from pathlib import Path

# Ensure correct command-line arguments
if len(sys.argv) < 2:
  print("Usage: python -m models.<model_id>.publisher '<ohlc_json>'")
  sys.exit(1)

ohlc_json = sys.argv[1]

# Load model
model_path = Path(__file__).parent / "model"
model = PPO.load(model_path)

def evaluate_with_model(json_str):
  return '{"action": "BUY", "symbol": "USDJPY", "price": 1.1}'
  # try:
  #   data_list = json.loads(json_str)
  #   df = pd.DataFrame(data_list)

  #   df.drop(columns=['time'], errors='ignore', inplace=True)
  #   df.rename(columns={"volumn": "tick_volume"}, inplace=True)

  #   numeric_cols = ['open', 'high', 'low', 'close']
  #   df[numeric_cols] = df[numeric_cols].astype(float)

  #   if len(df) < 109:
  #     ServerLogHelper().log(f"Not enough data. Received only {len(df)} rows.")
  #     return "ERROR"

  #   df['EMA_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
  #   df['EMA_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
  #   df['MACD'] = MACD(df['close']).macd()
  #   df['RSI'] = RSIIndicator(df['close']).rsi()
  #   bb = BollingerBands(df['close'], window=20)
  #   df['BB_Upper'] = bb.bollinger_hband()
  #   df['BB_Lower'] = bb.bollinger_lband()

  #   df = df.dropna()

  #   if len(df) < 60:
  #     ServerLogHelper().log(f"Invalid data shape after indicators: {df.shape}. Expected (60, 11).")
  #     return "ERROR"

  #   df = df.tail(60)

  #   action_signal, _ = model.predict(df.values, deterministic=True)
  #   ServerLogHelper().log(f"Predicted action signal: {action_signal}")

  #   action_signal = int(action_signal)
  #   action_map = {0: "hold", 1: "buy", 2: "sell", 3: "close_buy", 4: "close_sell"}
  #   return action_map.get(action_signal, "ERROR")

  # except Exception as e:
  #   ServerLogHelper().log(f"Error in evaluate_with_model: {e}")
  #   return "ERROR"

result = evaluate_with_model(ohlc_json)
print(result, flush=True)

