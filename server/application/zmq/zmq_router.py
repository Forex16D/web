import sys
import zmq
import json
import time
import requests
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
from application.services.portfolio_service import PortfolioService
from application.container import container
from concurrent.futures import ThreadPoolExecutor  # Import the ThreadPoolExecutor
from application.container import container
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

prediction_cache = {}
cache_expiry_seconds = 5

clients = {}
identity_to_portfolio = {} 
HEARTBEAT_TIMEOUT = 60

context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket_publisher = context.socket(zmq.PUB)

socket.bind("tcp://*:5557")
socket_publisher.bind("tcp://*:5555")

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

executor = ThreadPoolExecutor(max_workers=3)

print("ZeroMQ server is running...")

MODEL_CACHE = {}

def load_model(model_path):
  """
  Load model only once and cache it
  """
  # Convert to string path for consistent dictionary key
  model_path_str = str(model_path)
  
  if model_path_str not in MODEL_CACHE:
    try:
      MODEL_CACHE[model_path_str] = PPO.load(model_path)
      print(f"Model loaded from {model_path}")
    except Exception as e:
      print(f"Error loading model from {model_path}: {e}")
      return

  return MODEL_CACHE[model_path_str]

def evaluate_with_model(ohlc_json, model):
  try:
    data_list = json.loads(ohlc_json)

    df = pd.DataFrame(data_list)
    df.drop(columns=['time'], errors='ignore', inplace=True)

    numeric_cols = ['open', 'high', 'low', 'close', 'tick_volume']
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

    adx_indicator = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
    df['ADX'] = adx_indicator.adx()
    df['ADX_Positive'] = adx_indicator.adx_pos()
    df['ADX_Negative'] = adx_indicator.adx_neg()
    
    df.dropna(inplace=True)

    if len(df) < 60:
      print(f"Error: Invalid data shape after indicators {df.shape}")
      sys.exit(1)

    action_signal, _ = model.predict(df.values.astype(np.float32), deterministic=True)
    
    action_map = {0: "hold", 1: "open_long", 2: "open_short"}
    return action_map.get(int(action_signal), "ERROR")

  except Exception as e:
    print(f"ERROR: {e}", flush=True)

def run_prediction(model_id, data):
  model_path = f"/app/models/{model_id}/model"
  model = load_model(model_path)
  action = evaluate_with_model(data, model)
  prediction = json.dumps({"action": action})
  return bytes(prediction, "utf-8")

while True:
  try:
    events = dict(poller.poll(timeout=100))  # 100ms timeout

    if socket in events:
      identity, message = socket.recv_multipart()
      message_str = message.decode("utf-8", "ignore")
      
      if not message_str.strip():
        continue

      print(f"Received from {identity.hex()}")
      response = None
      clients[identity] = time.time()

      if "signal_request" in message_str:
        try:
          data = json.loads(message_str)
          if isinstance(data, str):
            data = json.loads(data)
        except json.JSONDecodeError as e:
          print(f"JSON Decode Error: {e} | Raw: {message_str}")
          data = None

        is_expert = False
        is_banned = container.user_service.check_ban_status_from_portfolio(data.get("portfolio_id"))
        if is_banned:
          response = b"User is banned!"
        
        if not data:
          response = b"No data found!"

        model_id = data.get("model_id")
        is_expert = bool(data.get("is_expert"))  
        portfolio_id = data.get("portfolio_id")
        market_data = data.get("market_data")
        identity_to_portfolio[identity] = portfolio_id  # Store mapping

        current_time = time.time()

        # ✅ **Remove expired cache**
        expired_keys = [key for key, (_, timestamp) in prediction_cache.items() if current_time - timestamp > cache_expiry_seconds]
        for key in expired_keys:
          del prediction_cache[key]

        # ✅ **Use cached response if available**
        if model_id in prediction_cache and current_time - prediction_cache[model_id][1] < cache_expiry_seconds:
          response = prediction_cache[model_id][0]
        else:
          # Run prediction in a separate thread
          def handle_prediction_result(response):
              # When prediction is done, store it in cache and send the response
              prediction_cache[model_id] = (response, current_time)
              socket.send_multipart([identity, response])
              print(f"Sent to {identity.hex()}: {response}")
              # 🟠 **Publish signals if expert**
              if is_expert:
                socket_publisher.send_multipart([model_id.encode(), response])
                print(f"Published: {response}")
          
          response = run_prediction(model_id, market_data)

      elif "backtest" in message_str:
        try:
          data = json.loads(message_str)
          if isinstance(data, str):
            data = json.loads(data)
        except json.JSONDecodeError as e:
          print(f"JSON Decode Error: {e} | Raw: {message_str}")
          data = None

        if not data:
          response = b"No data found!"

        model_id = data.get("model_id")
        is_expert = bool(data.get("is_expert"))  
        portfolio_id = data.get("portfolio_id")
        market_data = data.get("market_data")
        identity_to_portfolio[identity] = portfolio_id

        def handle_prediction_result(response):
          socket.send_multipart([identity, response])
          print(f"Sent to {identity.hex()}: {response}")

        response = run_prediction(model_id, market_data)

      # 🔵 **Handle Client Initialization**
      elif "init" in message_str or "heartbeat" in message_str:
        portfolio_id = message_str.split(" ")[-1]
        PortfolioService.update_connection_status(container.db_pool, portfolio_id, True)
        identity_to_portfolio[identity] = portfolio_id  # Store identity mapping
        response = b"Connection established..."

      # 🟡 **Process Orders**
      elif "order" in message_str:
        try:
          data = json.loads(message_str)
          if isinstance(data, str):
            data = json.loads(data)
        except json.JSONDecodeError as e:
          print(f"JSON Decode Error: {e} | Raw: {message_str}")
          data = None

        if data:
          token = data.pop("token", None)
          headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
          requests.post("http://localhost:5000/v1/mt/order", json=data, headers=headers)

      # 🔴 **Handle Client Disconnection**
      elif "end" in message_str:
        portfolio_id = message_str.split(" ")[-1]
        PortfolioService.update_connection_status(container.db_pool, portfolio_id, False)
        response = b"Closing connection..."
        identity_to_portfolio.pop(identity, None)  # Remove mapping

      # ✅ **Send response back to client** (This is done once prediction is complete)
      if response:
        socket.send_multipart([identity, response])
        print(f"Sent to {identity.hex()}: {response}")

        # 🟠 **Publish signals if expert**
        if "signal_request" in message_str or "backtest" in message_str and is_expert:
          socket_publisher.send_multipart([portfolio_id.encode(), response])
          print(f"Published: {response}")

    # 🔍 **Detect Disconnected Clients**
    now = time.time()
    disconnected_clients = [client for client, last_seen in clients.items() if now - last_seen > HEARTBEAT_TIMEOUT]

    for client in disconnected_clients:
      portfolio_id = identity_to_portfolio.get(client)
      if portfolio_id:
        print(f"Client {client.hex()} (Portfolio: {portfolio_id}) disconnected!")
        PortfolioService.update_connection_status(container.db_pool, portfolio_id, False)
        del identity_to_portfolio[client]  # Remove mapping
      del clients[client]  # Remove from active list

    time.sleep(0.001)  # Prevent CPU overuse

  except KeyboardInterrupt:
    print("Server shutting down...")
    break
