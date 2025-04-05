from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor # type: ignore
import hmac
import hashlib
import base64
import os
from application.helpers.server_log_helper import *
from application.services.bot_token_service import *

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY_BOT_TOKEN")

class MtService:
  def __init__(self, db_pool):
    self.db_pool = db_pool

  def verify_token(self, request):
    token = None
    auth_header = None
    if "Authorization" in request.headers:
      auth_header = request.headers["Authorization"]

    if not auth_header:
      raise ValueError()
  
    if auth_header.startswith("Bearer "):
      token = auth_header.split(" ")[1]

    decoded = base64.urlsafe_b64decode(token.encode())
    payload, received_signature = decoded.rsplit(b".", 1)
    key = SECRET_KEY.encode() if isinstance(SECRET_KEY, str) else SECRET_KEY
    expected_signature = hmac.new(key, payload, hashlib.sha256).digest()

    if hmac.compare_digest(expected_signature, received_signature):
      try:
        conn = self.db_pool.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
          SELECT portfolio_id, model_id, expert_id, is_expert, is_banned
          FROM portfolios 
          LEFT JOIN users ON portfolios.user_id = users.user_id
          WHERE portfolio_id = (
            SELECT portfolio_id 
            FROM tokens 
            WHERE access_token = %s 
            AND is_active = true
          );
        """, (token,))
        credential = cursor.fetchone()

        if credential["is_banned"]:
          raise ValueError("User has unpaid bills")

        return credential
      except ValueError as e:
        raise e
      except Exception as e:
        raise Exception("Token verification failed:", e)
      finally:
        cursor.close()
        self.db_pool.release_connection(conn)
    return None
  
  def create_order(self, request):
    try:
      data = request.get_json()
      if not data:
        raise ValueError("Invalid request data")
      
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)

      cursor.execute("""
        SELECT commission FROM models WHERE model_id = %s
        UNION
        SELECT commission FROM portfolios WHERE portfolio_id = %s
      """,
      (data["model_id"], data["model_id"])
      )

      commission = cursor.fetchone()

      query = """
      INSERT INTO orders 
      (order_id, portfolio_id, model_id, order_type, symbol, profit, volume, entry_price, exit_price, created_at, comission) 
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s);
      """

      cursor.execute(query, (
        data["order_id"], 
        data["portfolio_id"], 
        data["model_id"], 
        data["order_type"].lower(), 
        data["symbol"], 
        data["profit"], 
        data["volume"], 
        data["entry_price"], 
        data["exit_price"],
        commission
      ))

      conn.commit()
      return {"message": "Order recorded successfully"}

    except Exception as e:
      conn.rollback()
      raise e

    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
