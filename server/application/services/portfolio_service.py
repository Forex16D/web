from flask import jsonify # type: ignore
from psycopg2.extras import RealDictCursor # type: ignore
from datetime import datetime, timedelta
import calendar
import uuid
import application.services.bot_token_service as bot_token_service

class PortfolioService:
  def __init__(self, db_pool):
    self.db_pool = db_pool

  def get_portfolios_by_user(self, user_id):
    conn = self.db_pool.get_connection()
    try:
      now = datetime.now()
      first_day = now.replace(day=1).strftime('%Y-%m-%d')
      last_day = now.replace(day=calendar.monthrange(now.year, now.month)[1]).strftime('%Y-%m-%d')

      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("""
        SELECT 
            portfolios.*, 
            models.name AS model_name,
            -- Calculate the total profit for the entire month
            COALESCE(SUM(orders.profit), 0) AS total_profit,
            -- Calculate the monthly PnL for the current month only
            COALESCE(SUM(
                CASE 
                    WHEN orders.created_at BETWEEN %s AND %s 
                    THEN orders.profit 
                    ELSE 0 
                END
            ), 0) AS monthly_pnl,
            -- Calculate the winrate (percentage of winning orders in the entire month)
            CASE 
                WHEN COUNT(orders.profit) > 0 THEN 
                    (SUM(CASE WHEN orders.profit >= 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(orders.profit))
                ELSE 
                    0
            END AS winrate
        FROM 
            portfolios
        LEFT JOIN 
            models ON portfolios.model_id = models.model_id
        LEFT JOIN 
            orders ON orders.portfolio_id = portfolios.portfolio_id
        WHERE 
            portfolios.user_id = %s
        GROUP BY 
            portfolios.portfolio_id, models.name
        ORDER BY 
            portfolios.created_at ASC;
      """, (first_day, last_day, user_id))

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
    is_expert = data.get("is_expert")

    if not name or not login:
      raise ValueError("Missing required information.")

    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("""
        UPDATE portfolios 
        SET name = %s, login = %s, is_expert = %s
        WHERE portfolio_id = %s;
      """, (name, login, is_expert, str(portfolio_id)))
      conn.commit()

      return {"message": "Portfolio Updated Successfully!"}

    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(str(e)) 
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  @staticmethod
  def update_connection_status(db_pool, portfolio_id, status):
    conn = db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("UPDATE portfolios SET connect = %s WHERE portfolio_id = %s", (status, str(portfolio_id)))
      conn.commit()

      return {"message": "Connection Status Updated Successfully!"}

    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(str(e)) 
    finally:
      cursor.close()
      db_pool.release_connection(conn)