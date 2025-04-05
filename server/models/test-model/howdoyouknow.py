import gymnasium as gym
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from gymnasium.spaces import Discrete, Box
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from pathlib import Path
from tvDatafeed import TvDatafeed, Interval
from dotenv import load_dotenv
import os

load_dotenv()

class StockTradingEnv(gym.Env):
  def __init__(self, data, window_size=60, initial_balance=10000, volume=100):
    super(StockTradingEnv, self).__init__()
    self.initial_balance = initial_balance
    self.max_drawdown_pct = 0.1
    self.data = data
    self.window_size = window_size
    self.current_step = window_size
    self.balance = initial_balance
    self.positions = []
    self.volume = volume
    self.min_hold_time = 10
    self.stop_loss_threshold = 0.01
    self.profit_take_threshold = 0.01
    self.action_space = Discrete(3)  # 0: Hold, 1: Open Long Close Short, 2: Open short Close long 
    self.observation_space = Box(low=-np.inf, high=np.inf, shape=(self.window_size, 14), dtype=np.float32)

  def step(self, action):
    current_price = self.data['close'].iloc[self.current_step]
    reward = 0
    realized_reward = 0
    holding_reward = 0

    current_drawdown = (self.initial_balance - self.balance) / self.initial_balance
    if current_drawdown > self.max_drawdown_pct:
      done = True
      reward
      print("❌ Max drawdown exceeded. Ending episode.")
      return None, reward, True, False, {}

    if action == 1 and self.balance >= current_price * self.volume:
      print("🔁 Switching to LONG")
      new_positions = []
      total_profit = 0
      for position in self.positions:
        if position[0] == "sell":  # Closing short
          entry_price = position[1]
          cost_basis = entry_price * self.volume
          profit = (entry_price - current_price) * self.volume
          self.balance += cost_basis + profit
          
          r = profit / (self.volume * current_price)
          realized_reward += r
          total_profit += profit
          print(f"""💸 Closed SHORT:
            📉 Entry Price: {entry_price}
            📈 Exit Price: {current_price}
            💰 Cost Basis: {cost_basis:.2f}
            💸 Profit: {profit:.2f}
            🎯 Reward: {r:.4f}
          """)
        else:
          new_positions.append(position)
      print(f"💰 Total Profit from closed positions: {total_profit}")
      self.positions = new_positions
      self.positions.append(["buy", current_price, self.current_step])
      self.balance -= current_price * self.volume
      print(f"🟢 Opened LONG at {current_price}")

    elif action == 2 and self.balance >= current_price * self.volume:
      print("🔁 Switching to SHORT")
      new_positions = []
      total_profit = 0
      for position in self.positions:
        if position[0] == "buy":  # Closing long
          entry_price = position[1]
          cost_basis = entry_price * self.volume
          profit = (current_price - entry_price) * self.volume
          self.balance += cost_basis + profit

          r = profit / (self.volume * current_price)
          realized_reward += r
          total_profit += profit
          print(f"""💸 Closed LONG:
            📉 Entry Price: {entry_price}
            📈 Exit Price: {current_price}
            💰 Cost Basis: {cost_basis}
            💸 Profit: {profit}
            🎯 Reward: {r:.4f}
          """)
        else:
          new_positions.append(position)
      print(f"💰 Total Profit from closed positions: {total_profit}")
      self.positions = new_positions
      self.positions.append(["sell", current_price, self.current_step])
      self.balance -= current_price * self.volume
      print(f"🔴 Opened SHORT at {current_price}")

    if self.positions:
      unrealized_profit = sum(
        ((current_price - p[1]) * self.volume if p[0] == "buy" 
          else (p[1] - current_price) * self.volume)
        for p in self.positions
      )
      position_value = sum(p[1] * self.volume for p in self.positions)
      print(f"position_value: {position_value}")
      holding_reward = np.clip(unrealized_profit / (position_value * 0.1), -1, 1)
      print(f"📊 Holding positions: Unrealized Profit: {unrealized_profit}, Reward: {holding_reward:.4f}")

    # Combine all rewards
    reward = realized_reward + holding_reward

    # Move to the next step
    self.current_step += 1
    done = self.current_step >= len(self.data) - 1
    truncated = False
    state = self.data.iloc[self.current_step - self.window_size:self.current_step][
      ['EMA_12', 'EMA_50', 'MACD', 'RSI', 'BB_Upper', 'BB_Lower', 'ADX',
      'ADX_Positive', 'ADX_Negative', 'open', 'high', 'low', 'close', 'tick_volume']
    ].values

    print(f"""
  📊 Step: {self.current_step}
  📌 Action Taken: {'Buy (Long)' if action == 1 else 'Sell (Short)' if action == 2 else 'Hold'}
  🔹 Current Price: {current_price}
  🔹 Position Price: {current_price} * {self.volume} = {current_price * self.volume}
  🔹 Balance: {self.balance:.2f}
  🔹 Current Drawdown: {current_drawdown:.4f}
  🔹 Positions: {self.positions}
  🧮 Reward Summary:
    ▫️ Realized Reward: {realized_reward:.4f}
    ▫️ Holding Reward: {holding_reward:.4f}
    ✅ Total Step Reward: {reward:.4f}
  """)

    return state, reward, done, truncated, {}

  def reset(self, seed=None, **kwargs):
    if seed is not None:
      np.random.seed(seed)  # Optional: Set the seed for randomness

    self.current_step = self.window_size
    self.balance = 10000
    self.positions = []
    return self.data.iloc[self.current_step - self.window_size:self.current_step].values, {}

def get_new_data():
  username = os.getenv("TV_EMAIL")
  password = os.getenv("TV_PASSWORD")

  tv = TvDatafeed(username, password)
  symbol = "EURUSD"
  exchange = "OANDA"  
  interval = Interval.in_1_hour

  df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=6000)

  if df is None or df.empty:
    print("Error: No data received from TradingView")
    return None

  df.reset_index(drop=True, inplace=True)
  df.rename(columns={"volume": "tick_volume"}, inplace=True)
  df = df.drop(columns=['symbol'])

  return df

def load_data_from_csv(csv_path):
  df = pd.read_csv(csv_path, header=None)
  column_names = ["date", "time", "open", "high", "low", "close", "tick_volume", "volume", "spread"]
  df.columns = column_names[:df.shape[1]]
  return df

def create_indicator(df): 
    if 'date' in df.columns:
        df = df.drop(columns=['date'])
    if 'time' in df.columns:
        df = df.drop(columns=['time'])

    df = df.apply(pd.to_numeric, errors='coerce')

    df['EMA_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
    df['EMA_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['MACD'] = MACD(df['close']).macd()
    df['RSI'] = RSIIndicator(df['close']).rsi()

    bb = BollingerBands(df['close'], window=20)
    df['BB_Upper'] = bb.bollinger_hband()
    df['BB_Lower'] = bb.bollinger_lband()

    adx_indicator = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
    df['ADX'] = adx_indicator.adx()
    df['ADX_Positive'] = adx_indicator.adx_pos()
    df['ADX_Negative'] = adx_indicator.adx_neg()

    df.dropna(inplace=True)

    return df[['EMA_12', 'EMA_50', 'MACD', 'RSI', 'BB_Upper', 'BB_Lower', 'ADX', 'ADX_Positive', 'ADX_Negative',  'open', 'high', 'low', 'close', 'tick_volume']]

# def make_env():
  # return StockTradingEnv(df[-80:])
  
if __name__ == '__main__':

  parent_dir = Path(__file__).parent.parent.parent
  csv_path = parent_dir / "train-data" / "eurusd.csv"
  data = load_data_from_csv(csv_path)

  df = create_indicator(data)

  model_dir = Path(__file__).parent / "model"
  model = PPO.load(model_dir)

  env = DummyVecEnv([lambda: StockTradingEnv(df[-80:])])
  obs = env.reset()
  while True:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    print("------------------------------------------------------------------------")
    if done:
      break
