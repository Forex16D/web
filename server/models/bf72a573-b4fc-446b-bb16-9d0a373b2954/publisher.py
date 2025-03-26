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
  try:
    data_list = json.loads(json_str)
    data_list = json.loads(data_list)

    if not isinstance(data_list, list):
      raise ValueError("Parsed data is not a list")
    if not all(isinstance(row, dict) for row in data_list):
      raise ValueError("Elements in data_list are not dictionaries")

    df = pd.DataFrame(data_list)

    if df.empty:
      return "Error: DataFrame is empty"

    df.drop(columns=['time'], errors='ignore', inplace=True)
    df.rename(columns={"volumn": "tick_volume"}, inplace=True)

    numeric_cols = ['open', 'high', 'low', 'close']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    if df[numeric_cols].isnull().any().any():
      return "Error: Non-numeric values found in OHLC data"

    if len(df) < 109:
      return f"Error: Not enough data (only {len(df)} rows)"

    df['EMA_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
    df['EMA_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['MACD'] = MACD(df['close']).macd()
    df['RSI'] = RSIIndicator(df['close']).rsi()
    bb = BollingerBands(df['close'], window=20)
    df['BB_Upper'] = bb.bollinger_hband()
    df['BB_Lower'] = bb.bollinger_lband()

    df.dropna(inplace=True)

    if len(df) < 60:
      return f"Error: Invalid data shape after indicators {df.shape}"

    df = df.tail(60)

    action_signal, _ = model.predict(df.values, deterministic=True)
    
    action_map = {0: "hold", 1: "buy", 2: "sell", 3: "close_buy", 4: "close_sell"}
    return action_map.get(int(action_signal), "ERROR")

  except Exception as e:
    return f"ERROR: {e}"

result = evaluate_with_model(ohlc_json)
print(result, flush=True)

