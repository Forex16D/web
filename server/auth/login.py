from flask import jsonify
from dotenv import load_dotenv
import jwt
import datetime
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

def login(request):
  auth = request.get_json()
  username = auth.get("email")
  password = auth.get("password")

  if username == "root@root" and password == "12345678":
    token = jwt.encode(
      {
        "user": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
      },
      SECRET_KEY,
      algorithm="HS256"
    )
    return jsonify({"token": token})
  else:
    return jsonify({"message": "Invalid username or password!"}), 401

  
