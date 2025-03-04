import gymnasium as gym
import yfinance as yf
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from gymnasium.spaces import Discrete, Box
import MetaTrader5 as mt5
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from pathlib import Path

if not mt5.initialize():
  raise Exception("MetaTrader 5 initialization failed!")

def fetch_data(symbol, timeframe, bars):
  two_years_ago = 365 * 2 * 24 # hours in a year * 2 years * 24 hours 
  rates = mt5.copy_rates_from_pos(symbol, timeframe, two_years_ago, bars)
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
  return df[['EMA_12', 'EMA_50', 'MACD', 'RSI', 'BB_Upper', 'BB_Lower', 'open', 'high', 'low', 'close', 'tick_volume']]

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
    self.action_space = Discrete(5)  # 0: Hold, 1: Buy, 2: Sell 3: Close Buy 4: Close Sell
    self.observation_space = Box(low=-np.inf, high=np.inf, shape=(self.window_size, 11), dtype=np.float32)

  def step(self, action):
    current_price = self.data['close'].iloc[self.current_step]
    reward = 0

    if action == 1 and self.balance >= current_price * self.volume:  # Buy
      if len(self.positions) <= 20:
        self.positions.append(["buy", current_price, self.current_step])
        self.balance -= current_price * self.volume
        reward = 0.02 

    elif action == 2 and self.balance >= current_price * self.volume:  # Sell
      if len(self.positions) <= 20:
        self.positions.append(["sell", current_price, self.current_step])
        self.balance -= current_price * self.volume
        reward = 0.02

    elif action == 3:  # Close Buy
      # Close the buy position if one exists
      buy_position = next((position for position in self.positions if position[0] == "buy"), None)
      if buy_position:
        hold_time = self.current_step - buy_position[2]
        self.positions.remove(buy_position)
        profit = (current_price - buy_position[1]) * self.volume
        self.balance += current_price * self.volume
        reward = np.sign(profit) * (abs(profit) ** 0.5)

        # if hold_time < self.min_hold_time:
        #   reward -= 0.1
      else:
        reward = -1.0  # Penalty for trying to close a buy that doesn't exist

    elif action == 4:  # Close Sell
      # Close the sell position if one exists
      sell_position = next((position for position in self.positions if position[0] == "sell"), None)
      if sell_position:
        hold_time = self.current_step - sell_position[2]
        self.positions.remove(sell_position)
        profit = (sell_position[1] - current_price) * self.volume
        self.balance += current_price * self.volume
        reward = np.sign(profit) * (abs(profit) ** 0.5)  

        # if hold_time < self.min_hold_time:
        #   reward -= 0.1
      else:
        reward = -0.1  # Penalty for trying to close a buy that doesn't exist

    else:
      if self.positions:
        unrealized_profit = sum(
          ((current_price - p[1]) * self.volume if p[0] == "buy" else (p[1] - current_price) * self.volume)
          for p in self.positions
        )
        reward = np.clip(unrealized_profit * 0.01 + 0.05, -1, 1)

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

  model = PPO("MlpPolicy", env, learning_rate=5e-5, batch_size=256, n_steps=4096, gamma=0.995, verbose=1)
  model.learn(total_timesteps=100000)
  script_dir = Path(__file__).parent
  file_path = script_dir / "model"
  model.save(str(file_path))
  mt5.shutdown()
