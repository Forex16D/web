from flask import jsonify
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import jwt
import datetime
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

def login(request, db_pool):
  auth = request.get_json()
  username = auth.get("email")
  password = auth.get("password")
  
  conn = db_pool.get_connection()
    
  try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s;", (username,))
    user = cursor.fetchone()
    cursor.close()

    if user and user["password"] == password:
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
  except Exception as e:
    print(e)
    return jsonify({"error": str(e)}), 500
  finally:
    db_pool.release_connection(conn)

  
