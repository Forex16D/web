from flask import jsonify
from psycopg2.extras import RealDictCursor
import jwt
import datetime
import uuid

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
      return jsonify({"error": "Email already exists"}), 400 
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
      return jsonify({"error": str(e)}), 500
  finally:
      db_pool.release_connection(conn)
