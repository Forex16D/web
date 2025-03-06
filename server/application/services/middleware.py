from flask import request, jsonify # type: ignore
from psycopg2.extras import RealDictCursor # type: ignore
import jwt # type: ignore
from functools import wraps
from dotenv import load_dotenv
import datetime
import os
import hmac
import hashlib
import base64

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY_BOT_TOKEN = os.getenv("SECRET_KEY_BOT_TOKEN")

def sign_token(user_id, role, remember=False):
  # if remember expire in 7 days
  time_offset = 168 if remember else 1
  token = jwt.encode(
    {
      "user": user_id,
      "role": role,
      "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=time_offset)
    },
    SECRET_KEY,
    algorithm="HS256"
  )
  return {"token": token}

def token_required(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    token = None
    if "Authorization" in request.headers:
      auth_header = request.headers["Authorization"]
      if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    try:
      data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
      current_user_id = data["user"]

      user_id_from_request = kwargs.get("user_id", None)

      if user_id_from_request and int(user_id_from_request) != current_user_id:
        return jsonify({"status": 403, "message": "Forbidden"}), 403

    except jwt.ExpiredSignatureError:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401
    except jwt.InvalidTokenError:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    return f(current_user_id, *args, **kwargs)
  
  return decorator

def admin_required(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    token = None
    if "Authorization" in request.headers:
      auth_header = request.headers["Authorization"]
      if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    try:
      data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
      current_user_role = data["role"]
      
      if current_user_role != "admin":
        return jsonify({"status": 403, "message": "Forbidden"}), 403

      current_user_id = data["user"]

    except jwt.ExpiredSignatureError:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401
    except jwt.InvalidTokenError:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    return f(current_user_id, *args, **kwargs)
  
  return decorator

def bot_token_required(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    token = None
    if "Authorization" in request.headers:
      auth_header = request.headers["Authorization"]
      if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    try:
      user_id = None
      portfolio_id = None

      decoded = base64.urlsafe_b64decode(token.encode())
      payload, received_signature = decoded.rsplit(b".", 1)
      key = SECRET_KEY.encode() if isinstance(SECRET_KEY, str) else SECRET_KEY
      expected_signature = hmac.new(key, payload, hashlib.sha256).digest()

      if hmac.compare_digest(expected_signature, received_signature):
        user_id, portfolio_id, _ = payload.rsplit(":")
    except jwt.ExpiredSignatureError:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401
    except jwt.InvalidTokenError:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    return f(user_id, portfolio_id, *args, **kwargs)
  
  return decorator
