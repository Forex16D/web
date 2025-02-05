from flask import request, jsonify
import jwt
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

def token_required(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    token = None
    if 'Authorization' in request.headers:
      auth_header = request.headers['Authorization']
      if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    try:
      data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
      current_user_id = data["user"]

      user_id_from_request = kwargs.get('user_id', None)

      if user_id_from_request and int(user_id_from_request) != current_user_id:
        return jsonify({"status": 403, "message": "Forbidden"}), 403

    except jwt.ExpiredSignatureError:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401
    except jwt.InvalidTokenError:
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    return f(current_user_id, *args, **kwargs)
  
  return decorator