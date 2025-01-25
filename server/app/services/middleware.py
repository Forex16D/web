from flask import request, jsonify
import jwt
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = request.headers.get('x-access-token')
    if not token:
      return jsonify({"message": "Token is missing!"}), 401
    try:
      data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
      current_user = data["user"]
    except jwt.ExpiredSignatureError:
      return jsonify({"message": "Token has expired!"}), 401
    except jwt.InvalidTokenError:
      return jsonify({"message": "Invalid token!"}), 401
    return f(current_user, *args, **kwargs)
  return decorated