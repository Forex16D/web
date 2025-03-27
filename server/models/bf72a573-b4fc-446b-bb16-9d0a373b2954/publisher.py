import sys
import json
import pandas as pd
from stable_baselines3 import PPO
from pathlib import Path
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

def main():
  if len(sys.argv) < 2:
    print("Usage: python -m models.<model_id>.publisher '<ohlc_json>'")
    sys.exit(1)

  ohlc_json = sys.argv[2]

  # Load model path dynamically
  model_path = Path(__file__).parent / "model"
  
  try:
    # Load and predict
    model = PPO.load(model_path)
    
    # Rest of your existing evaluation logic
    data_list = json.loads(ohlc_json)
    data_list = json.loads(data_list)

    df = pd.DataFrame(data_list)
    df.drop(columns=['time'], errors='ignore', inplace=True)

    numeric_cols = ['open', 'high', 'low', 'close']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    if len(df) < 109:
      print(f"Error: Not enough data (only {len(df)} rows)")
      sys.exit(1)

    df['EMA_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
    df['EMA_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['MACD'] = MACD(df['close']).macd()
    df['RSI'] = RSIIndicator(df['close']).rsi()
    bb = BollingerBands(df['close'], window=20)
    df['BB_Upper'] = bb.bollinger_hband()
    df['BB_Lower'] = bb.bollinger_lband()

    df.dropna(inplace=True)

    if len(df) < 60:
      print(f"Error: Invalid data shape after indicators {df.shape}")
      sys.exit(1)

    df = df.tail(60)

    action_signal, _ = model.predict(df.values, deterministic=True)
    
    action_map = {0: "hold", 1: "open_long", 2: "open_short"}
    print(action_map.get(int(action_signal), "ERROR"), flush=True)

  except Exception as e:
    print(f"ERROR: {e}", flush=True)

if __name__ == "__main__":
  main()