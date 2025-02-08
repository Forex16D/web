import os
from dotenv import load_dotenv
import hmac
import hashlib
import base64
import time
import uuid

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY_BOT_TOKEN")

def generate_bot_token(user_id, portfolio_id):
  nonce = str(uuid.uuid4())
  payload = f"{user_id}:{portfolio_id}:{nonce}:{int(time.time())}"

  key = SECRET_KEY.encode() if isinstance(SECRET_KEY, str) else SECRET_KEY

  signature = hmac.new(key, payload.encode(), hashlib.sha256).digest()
  token = base64.urlsafe_b64encode(payload.encode() + b"." + signature).decode()
  
  return token
