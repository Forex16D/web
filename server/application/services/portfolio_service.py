from flask import jsonify # type: ignore
from psycopg2.extras import RealDictCursor # type: ignore
import uuid
import application.services.bot_token_service as bot_token_service

class PortfolioService:
  def __init__(self, db_pool):
    self.db_pool = db_pool

  def get_portfolios_by_user(self, user_id):
    conn = self.db_pool.get_connection()
    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM portfolios WHERE user_id = %s ORDER BY created_at ASC", (user_id,))
      portfolios = cursor.fetchall()

      if not portfolios:
        raise ValueError("Not found")

      return portfolios
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(e) 
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def create_portfolio(self, data, user_id):
    name = data.get("name")
    login = data.get("login")
    
    if not name or not login or not user_id:
      raise ValueError("Missing required information.")

    conn = self.db_pool.get_connection()

    try:
      portfolio_id = uuid.uuid4()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("""
        INSERT INTO portfolios (portfolio_id, user_id, name, login) 
        VALUES (%s, %s, %s, %s)
      """, (str(portfolio_id), user_id, name, login))

      token = bot_token_service.generate_bot_token(user_id, str(portfolio_id))

      cursor.execute("""
        INSERT INTO tokens (portfolio_id, access_token)
        VALUES (%s, %s)
      """, (str(portfolio_id), token))
      conn.commit()

      return {"message": "Portfolio Created Successfully!"}

    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(str(e))
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def delete_portfolio(self, portfolio_id, user_id):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("DELETE FROM portfolios WHERE user_id=%s AND portfolio_id=%s", (user_id, portfolio_id))
      conn.commit()

      if cursor.rowcount == 0:
        raise ValueError("Portfolio not found.")

      return {"message": "Portfolio Deleted Successfully!"}

    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(f"Something went wrong {str(e)}") 
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def update_portfolio(self, data, portfolio_id):
    name = data.get("name")
    login = data.get("login")

    if not name or not login:
      raise ValueError("Missing required information.")

    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("""
        UPDATE portfolios 
        SET name = %s, login = %s
        WHERE portfolio_id = %s;
      """, (name, login, str(portfolio_id)))
      conn.commit()

      return {"message": "Portfolio Updated Successfully!"}

    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(str(e)) 
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
