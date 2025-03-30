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
            tokens.access_token,
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
            -- Calculate the winrate
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
        LEFT JOIN
            tokens ON tokens.portfolio_id = portfolios.portfolio_id
        WHERE 
            portfolios.user_id = %s
        GROUP BY 
            portfolios.portfolio_id, models.name, tokens.access_token
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

  def get_expert_portfolios(self):
    conn = self.db_pool.get_connection()
    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      now = datetime.now()
      first_day = now.replace(day=1).strftime('%Y-%m-%d')
      last_day = now.replace(day=calendar.monthrange(now.year, now.month)[1]).strftime('%Y-%m-%d')
      
      # Fetch portfolios with total profit and monthly pnl
      cursor.execute("""
      SELECT 
        portfolios.connected, 
        portfolios.created_at, 
        portfolios.is_expert, 
        portfolios.name, 
        portfolios.portfolio_id,
        portfolios.user_id,
        portfolios.commission,
        COALESCE(SUM(orders.profit), 0) AS total_profit,
        COALESCE(SUM(
          CASE 
            WHEN orders.created_at BETWEEN %s AND %s 
            THEN orders.profit 
            ELSE 0 
          END
        ), 0) AS monthly_pnl,
        CASE 
          WHEN COUNT(orders.profit) > 0 THEN 
            (SUM(CASE WHEN orders.profit >= 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(orders.profit))
          ELSE 
            0
        END AS winrate
      FROM portfolios
      LEFT JOIN models ON portfolios.model_id = models.model_id
      LEFT JOIN orders ON orders.portfolio_id = portfolios.portfolio_id
      WHERE portfolios.is_expert = true
      GROUP BY portfolios.portfolio_id
      ORDER BY portfolios.created_at DESC;
      """, (first_day, last_day))
      portfolios = cursor.fetchall()

      if not portfolios:
        raise ValueError("No expert portfolios found")
      
      # Fetch the last 8 weeks of weekly profit for each portfolio
      cursor.execute("""
      SELECT 
        portfolios.portfolio_id,
        weeks.week_start,
        COALESCE(SUM(orders.profit), 0) AS weekly_profit
      FROM (
        -- Generate the last 8 weeks
        SELECT generate_series(
          DATE_TRUNC('week', NOW()) - INTERVAL '7 weeks', 
          DATE_TRUNC('week', NOW()), 
          INTERVAL '1 week'
        ) AS week_start
      ) weeks
      LEFT JOIN portfolios ON true  -- Join each week to portfolios
      LEFT JOIN orders 
        ON orders.portfolio_id = portfolios.portfolio_id
        AND orders.created_at >= weeks.week_start 
        AND orders.created_at < weeks.week_start + INTERVAL '1 week'
      WHERE portfolios.is_expert = true
      GROUP BY portfolios.portfolio_id, weeks.week_start
      ORDER BY portfolios.portfolio_id, weeks.week_start ASC;
      """)
      weekly_profits = cursor.fetchall()

      # Associate weekly profits with their respective portfolios
      for portfolio in portfolios:
        portfolio['weekly_profits'] = [
          weekly_profit for weekly_profit in weekly_profits
          if weekly_profit['portfolio_id'] == portfolio['portfolio_id']
        ]

      return {"portfolios": portfolios}
    
    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(e)
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def get_total_commission(self, user_id):
    conn = self.db_pool.get_connection()
    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("""
        SELECT
          (COALESCE(SUM(orders.profit), 0) * portfolios.commission) AS total_profit, portfolios.name
        FROM orders
        JOIN portfolios ON orders.model_id = portfolios.portfolio_id
        WHERE portfolios.user_id = %s
        GROUP BY portfolios.portfolio_id
      """, (user_id,))
      result = cursor.fetchall()

      return result

    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(e)
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def get_portfolio_commission(self, portfolio_id):
    conn = self.db_pool.get_connection()
    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("""
        SELECT
          (COALESCE(SUM(profit), 0) * portfolios.commission) AS total_profit
        FROM orders
        JOIN portfolios ON orders.model_id = portfolios.portfolio_id
        WHERE portfolios.portfolio_id = %s
        GROUP BY portfolios.portfolio_id
      """, (portfolio_id,))
      result = cursor.fetchone()

      return result

    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(e)
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def get_user_balance(self, user_id):
    conn = self.db_pool.get_connection()
    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("""
        SELECT balance from users WHERE user_id = %s
      """, (user_id,))
      balance = cursor.fetchone()

      return balance

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
    commission = data.get("commission")

    if not name or not login:
      raise ValueError("Missing required information.")

    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("""
        UPDATE portfolios 
        SET name = %s, login = %s, is_expert = %s, commission = %s
        WHERE portfolio_id = %s;
      """, (name, login, is_expert, commission, str(portfolio_id)))
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
      cursor.execute("UPDATE portfolios SET connected = %s WHERE portfolio_id = %s", (status, str(portfolio_id)))
      conn.commit()

      return {"message": "Connection Status Updated Successfully!"}

    except ValueError as ve:
      raise ve
    except Exception as e:
      raise RuntimeError(str(e)) 
    finally:
      cursor.close()
      db_pool.release_connection(conn)