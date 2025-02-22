import gymnasium as gym
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from gymnasium.spaces import Discrete, Box
import MetaTrader5 as mt5
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

if not mt5.initialize():
  raise Exception("MetaTrader 5 initialization failed!")

def fetch_data(symbol, timeframe, bars):
  rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
  if rates is None or len(rates) == 0:
    raise Exception(f"No data retrieved for symbol: {symbol}")
  
  df = pd.DataFrame(rates)
  df['EMA_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
  df['EMA_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
  df['MACD'] = MACD(df['close']).macd()
  df['RSI'] = RSIIndicator(df['close']).rsi()
  bb = BollingerBands(df['close'], window=20)
  df['BB_Upper'] = bb.bollinger_hband()
  df['BB_Lower'] = bb.bollinger_lband()
  df.dropna(inplace=True)
  return df[['EMA_12', 'EMA_50', 'MACD', 'RSI', 'BB_Upper', 'BB_Lower', 'close', 'open', 'high', 'low']]

class StockTradingEnv(gym.Env):
  def __init__(self, data, window_size=60, initial_balance=10000, volume=100):
    super(StockTradingEnv, self).__init__()
    self.data = data
    self.window_size = window_size
    self.current_step = window_size
    self.balance = initial_balance
    self.positions = []
    self.volume = volume
    self.action_space = Discrete(3)  # 0: Hold, 1: Buy, 2: Sell
    self.observation_space = Box(low=-np.inf, high=np.inf, shape=(self.window_size, 10), dtype=np.float32)

  def step(self, action):
    current_price = self.data['close'].iloc[self.current_step]
    reward = 0

    if action == 1 and self.balance >= current_price * self.volume:  # Buy
      self.positions.append(current_price)
      self.balance -= current_price * self.volume
      reward = 0.1 
    elif action == 2 and self.positions:  # Sell
      entry_price = self.positions.pop(0)
      profit = (current_price - entry_price) * self.volume
      reward = profit
      self.balance += current_price * self.volume
    else:
      if self.positions:
        unrealized_profit = (current_price - self.positions[0]) * self.volume
        reward = unrealized_profit / 10
      else:
        reward = -1


    self.current_step += 1
    done = self.current_step >= len(self.data) - 1
    truncated = False
    state = self.data.iloc[self.current_step - self.window_size:self.current_step].values if not done else self.data.iloc[self.current_step - self.window_size:self.current_step].values

    return state, reward, done, truncated, {}

  def reset(self, seed=None, **kwargs):
    if seed is not None:
      np.random.seed(seed)  # Optional: Set the seed for randomness

    self.current_step = self.window_size
    self.balance = 10000
    self.positions = []
    return self.data.iloc[self.current_step - self.window_size:self.current_step].values, {}

if __name__ == '__main__':
  symbol = "EURUSD"
  timeframe = mt5.TIMEFRAME_H1
  data = fetch_data(symbol, timeframe, 100000)
  env = DummyVecEnv([lambda: StockTradingEnv(data)])

  model = PPO("MlpPolicy", env, learning_rate=1e-4, batch_size=128, n_steps=2048, gamma=0.98, verbose=1)
  model.learn(total_timesteps=100000)
  model.save("./server/models/output/ppo_trading_model")
  mt5.shutdown()
