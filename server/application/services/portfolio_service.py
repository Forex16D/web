from flask import jsonify
from psycopg2.extras import RealDictCursor
import jwt
import logging

class PortfolioService:
  def __init__(self, db_pool):
    self.db_pool = db_pool

  def get_portfolios_by_user(self, user_id):
    conn = self.db_pool.get_connection()
    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM portfolios WHERE user_id = %s", (user_id,))
      portfolios = cursor.fetchall()
      cursor.close()

      if not portfolios:
        raise ValueError("Not found")

      return portfolios
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Something went wrong") 
    finally:
      self.db_pool.release_connection(conn)
  