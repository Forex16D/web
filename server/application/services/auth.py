from flask import jsonify
from psycopg2.extras import RealDictCursor
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
import jwt
import datetime
import os
import uuid

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def login(request, db_pool, hasher):
  data = request.get_json()
  email = data.get("email")
  password = data.get("password")

  conn = db_pool.get_connection()

  try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT password, user_id FROM users WHERE email = %s;", (email,))
    user = cursor.fetchone()
    cursor.close()

    if user:
      try:
        if hasher.verify(user["password"], password):
          token = jwt.encode(
            {
              "user": user["user_id"],
              "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            },
            SECRET_KEY,
            algorithm="HS256"
          )
          return jsonify({"token": token})
      except VerifyMismatchError:
        pass
    return jsonify({"message": "Invalid email or password!"}), 401
  except Exception as e:
    return jsonify({"message": "Something went wrong"}), 500
  finally:
    db_pool.release_connection(conn)
    
def register(request, db_pool, hasher):
  auth = request.get_json()
  email = auth.get("email")
  password = auth.get("password")
  confirm_password = auth.get("confirmPassword")

  if (password != confirm_password):
    return "Passwords not match", 400

  userId = uuid.uuid4()
  hashed_password = hasher.hash(password)
  conn = db_pool.get_connection()
  
  try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
    user = cursor.fetchone()
    cursor.close()
    
    if user:
      return jsonify({"message": "Email already exists"}), 400 
    else:
      cursor = conn.cursor()
      cursor.execute("""
        INSERT INTO users (user_id, email, password) 
        VALUES (%s, %s, %s)
      """, (str(userId), email, hashed_password))
      conn.commit()
      cursor.close()

      return jsonify({"message": "User registered successfully!"}), 201
  except Exception as e:
    return jsonify({"error": "Something went wrong"}), 500
  finally:
    db_pool.release_connection(conn)