from flask import jsonify
from psycopg2.extras import RealDictCursor
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
import jwt
import datetime
import os
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

def login(request, db_pool, hasher):
  auth = request.get_json()
  username = auth.get("email")
  password = auth.get("password")
  
  conn = db_pool.get_connection()
    
  try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT password FROM users WHERE email = %s;", (username,))
    password_db = cursor.fetchone()
    cursor.close()

    if password_db:
      try:
        if hasher.verify(password_db["password"], password):
          token = jwt.encode(
            {
              "user": username,
              "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            },
            SECRET_KEY,
            algorithm="HS256"
          )
          return jsonify({"token": token})
      except VerifyMismatchError:
        pass
    return jsonify({"error": "Invalid username or password!"}), 401
  except Exception as e:
    print(e)
    return jsonify({"error": str(e)}), 500
  finally:
    db_pool.release_connection(conn)

  
