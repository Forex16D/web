from flask import json # type: ignore
import sys
import gymnasium as gym
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
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
    self.data = data
    self.window_size = window_size
    self.current_step = window_size
    self.balance = initial_balance
    self.positions = []
    self.volume = volume
    self.min_hold_time = 10
    self.action_space = Discrete(3)  # 0: Hold, 1: Open Long Close Short, 2: Open short Close long 
    self.observation_space = Box(low=-np.inf, high=np.inf, shape=(self.window_size, 14), dtype=np.float32)

  def step(self, action):
    current_price = self.data['close'].iloc[self.current_step]
    reward = 0

    # Close existing short positions & open long
    if action == 1 and self.balance >= current_price * self.volume:  
      new_positions = []
      for position in self.positions:
        if position[0] == "sell":  # Closing short
          profit = (position[1] - current_price) * self.volume
          self.balance += profit
          reward += np.sign(profit) * (abs(profit) ** 0.5)
        else:
          new_positions.append(position)  # Keep other positions
      self.positions = new_positions
      
      # Open a long position
      self.positions.append(["buy", current_price, self.current_step])
      self.balance -= current_price * self.volume

    # Close existing long positions & open short
    elif action == 2 and self.balance >= current_price * self.volume:  
      new_positions = []
      for position in self.positions:
        if position[0] == "buy":  # Closing long
          profit = (current_price - position[1]) * self.volume
          self.balance += profit
          reward += np.sign(profit) * (abs(profit) ** 0.5)
        else:
          new_positions.append(position)
      self.positions = new_positions
      
      # Open a short position
      self.positions.append(["sell", current_price, self.current_step])
      self.balance -= current_price * self.volume

    # Hold & Calculate Unrealized Profit
    else:
      if self.positions:
        unrealized_profit = sum(
          ((current_price - p[1]) * self.volume if p[0] == "buy" 
            else (p[1] - current_price) * self.volume)
          for p in self.positions
        )
        reward = np.clip(unrealized_profit * 0.01 + 0.05, -1, 1)

    # Move to the next step
    self.current_step += 1
    done = self.current_step >= len(self.data) - 1
    truncated = False
    state = self.data.iloc[self.current_step - self.window_size:self.current_step].values

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
  print(df)

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
#   return StockTradingEnv(df[:149002])

if __name__ == '__main__':

  # if len(sys.argv) != 2:
  #   print("Usage: python3 train_model.py <temp_file_path>")
  #   sys.exit(1)

  # temp_file_path = sys.argv[1]

  # data = load_data_from_temp_file(temp_file_path)

  option = None

  if len(sys.argv) > 1:
    option = sys.argv[1]

  if (option == "auto"):
    data = get_new_data()
  else:
    parent_dir = Path(__file__).parent.parent.parent
    csv_path = parent_dir / "train-data" / "eurusd.csv"
    data = load_data_from_csv(csv_path)

  # df = create_indicator(data)
  # print(df)
  # # env = DummyVecEnv([lambda: StockTradingEnv(df[:149002])])
  # env = SubprocVecEnv([make_env for _ in range(5)])

  # policy_kwargs = dict(net_arch=[128, 64, 32, 32])
  # model = PPO('MlpPolicy',
  #               env, 
  #               verbose=1,
  #               learning_rate=5e-5,  
  #               gamma=0.975, 
  #               gae_lambda=0.935,
  #               ent_coef=0.03,
  #               n_epochs=5,
  #               # target_kl=0.01,
  #               # clip_range_vf=0.4,
  #               vf_coef=0.325,
  #               clip_range=0.35,  
  #               batch_size=256,        
  #               n_steps=4096,    
  #               policy_kwargs=policy_kwargs
  #              )

  # model.learn(total_timesteps=320000)
  # print("finished training")
  # script_dir = Path(__file__).parent
  # file_path = script_dir / "model"
  # model.save(str(file_path))

