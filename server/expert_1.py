import gym
from gym import spaces
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

class ForexTradingEnv(gym.Env):
  def __init__(self, data, initial_balance=10000, max_position_size=1.0):
    super(ForexTradingEnv, self).__init__()
    self.data = data
    self.initial_balance = initial_balance
    self.max_position_size = max_position_size

    # Define action space: [0: Hold, 1: Buy, 2: Sell, 3: Close Position]
    self.action_space = spaces.Discrete(4)

    # Observation space: Feature vector representing the market state
    self.observation_space = spaces.Box(
        low=-np.inf, high=np.inf, shape=(self.data.shape[1],), dtype=np.float32
    )

    self.reset()

  def reset(self):
    self.balance = self.initial_balance
    self.position_size = 0
    self.current_step = 0
    self.done = False
    self.profit = 0
    return self.data.iloc[self.current_step].values

  def step(self, action):
    reward = 0

    if action == 1:  # Buy
      self.open_position("buy")
    elif action == 2:  # Sell
      self.open_position("sell")
    elif action == 3:  # Close Position
      reward = self.close_position()

    # Update state and check if the episode is done
    self.current_step += 1
    if self.current_step >= len(self.data) - 1:
      self.done = True

    next_state = self.data.iloc[self.current_step].values
    return next_state, reward, self.done, {}

  def open_position(self, action_type, size=1.0):
    price = self.data.iloc[self.current_step]["CLOSE"]
    if action_type == "buy":
      self.balance -= size * price  # Deduct cost of the position
      self.position_size += size
    elif action_type == "sell":
      self.balance += size * price  # Add proceeds from the position
      self.position_size -= size

  def close_position(self):
    price = self.data.iloc[self.current_step]["CLOSE"]
    profit = self.position_size * price  # Calculate profit/loss
    self.balance += profit
    self.position_size = 0  # Reset position
    self.profit += profit
    return profit  # Use profit as reward

  def render(self, mode="human"):
    print(f"Step: {self.current_step}, Balance: {self.balance}, Position Size: {self.position_size}, Profit: {self.profit}")
    
if __name__ == "__main__":
  # Load dummy forex data

  data = pd.DataFrame({
      "OPEN": np.random.rand(1000) + 1.1,
      "HIGH": np.random.rand(1000) + 1.2,
      "LOW": np.random.rand(1000) + 1.0,
      "CLOSE": np.random.rand(1000) + 1.15,
      "VOLUME": np.random.randint(100, 200, 1000),
  })

  # data = pd.read_csv('EURUSD_H1.csv', delimiter='\t')
  # data.columns = [col.replace('<', '').replace('>', '') for col in data.columns]
  # data = data.drop(["DATE","TIME"],axis=1)
  # print(data)

  # Wrap the environment
  env = DummyVecEnv([lambda: ForexTradingEnv(data)])

  # Initialize the PPO model
  model = PPO("MlpPolicy", env, verbose=1)

  # Train the model
  model.learn(total_timesteps=10000)

  # Save the model
  # model.save("ppo_forex_trader")

  # model = PPO.load("ppo_forex_trader")

  # Test the model
  env = ForexTradingEnv(data)  # Use the base environment for testing
  obs = env.reset()
  for _ in range(500):
    action, _states = model.predict(obs)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
      break