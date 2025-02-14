from psycopg2.extras import RealDictCursor # type: ignore
from argon2.exceptions import VerifyMismatchError # type: ignore
from application.services.middleware import sign_token
import logging
import uuid


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

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"Attempting login for: {email}")

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
