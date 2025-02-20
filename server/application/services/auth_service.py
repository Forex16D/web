from psycopg2.extras import RealDictCursor # type: ignore
from argon2.exceptions import VerifyMismatchError # type: ignore
from application.services.middleware import sign_token
from application.helpers.logging import Logging
import uuid
from dotenv import load_dotenv
import jwt # type: ignore
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

class AuthService:
  def __init__(self, db_pool, hasher):
    self.db_pool = db_pool
    self.hasher = hasher

  def login(self, data):
    email = data.get("email").lower()
    password = data.get("password")
    remember = data.get("remember")
    
    if not email or not password:
      raise ValueError("Missing required information.")

    Logging.user_log(f"Attempting login for: {email}")

    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT password, user_id, role FROM users WHERE email = %s;", (email,))
      user = cursor.fetchone()

      if user:
        try:
          if self.hasher.verify(user["password"], password):
            return sign_token(user["user_id"], user["role"], remember)

        except VerifyMismatchError:
          raise ValueError("Invalid email or password!")
      raise ValueError("Invalid email or password!")

    except ValueError as ve:
      raise ve

    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")

    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def register(self, data): 
    email = data.get("email").lower()
    password = data.get("password")
    confirm_password = data.get("confirmPassword")
    
    if not email or not password or not confirm_password:
      raise ValueError("Missing required information.")
    
    if password != confirm_password:
      raise ValueError("Passwords do not match.")

    user_id = uuid.uuid4()
    hashed_password = self.hasher.hash(password)
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
      user = cursor.fetchone()

      if user:
        raise ValueError("Email already exists.")

      cursor.execute("""
        INSERT INTO users (user_id, email, password) 
        VALUES (%s, %s, %s)
      """, (str(user_id), email, hashed_password))
      conn.commit()
      return {"message": "User registered successfully!"}

    except ValueError as ve:
      raise ve
    
    except Exception as e:
      raise RuntimeError("An error occurred while registering the user.") from e

    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def verify_user(self, request):
    token = None
    if "Authorization" in request.headers:
      auth_header = request.headers["Authorization"]
      if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    if not token:
      raise ValueError

    try:
      data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
      current_user_id = data["user"]

      conn = self.db_pool.get_connection()
      
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (current_user_id,))
      user = cursor.fetchone()
      
      if not user:
        raise ValueError("User not found")
      
      return {"authentication": True}
    
    except jwt.ExpiredSignatureError as e:
      raise e
    except jwt.InvalidTokenError as e:
      raise e
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
