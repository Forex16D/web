from psycopg2.extras import RealDictCursor # type: ignore

class AdminService:
  def __init__(self, db_pool):
    self.db_pool = db_pool

  def get_dashboard(self):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)

      cursor.execute("""
        SELECT 
          (SELECT COUNT(user_id) FROM users) AS user_count, 
          (SELECT COUNT(model_id) FROM models) AS model_count,
          (SELECT COALESCE(SUM(amount_paid), 0) FROM receipts) AS revenue,
          (SELECT COUNT(model_id) FROM portfolios) AS subscriptions
      """)

      dashboard_data = cursor.fetchone()

      return {
          "total_users": dashboard_data["user_count"],
          "total_models": dashboard_data["model_count"],
          "total_revenue": dashboard_data["revenue"],
          "active_subscriptions": dashboard_data["subscriptions"],
      }
    
    except ValueError as ve:
      raise ve
    
    except Exception as e:
      raise RuntimeError("An error occurred while fetching the dashboard data.") from e

    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
      
  def get_revenue(self):
    try:
      conn = self.db_pool.get_connection()
      cursor = conn.cursor(cursor_factory=RealDictCursor)

      cursor.execute("""
        SELECT 
          DATE_TRUNC('month', payment_date) AS month, 
          COALESCE(SUM(amount_paid), 0) AS total_revenue
        FROM receipts
        WHERE payment_date >= NOW() - INTERVAL '9 months'
        GROUP BY month
        ORDER BY month ASC
      """)

      revenue_by_month = cursor.fetchall()

      return {
        "revenue_by_month": revenue_by_month
      }
    
    except ValueError as ve:
      raise ve
    
    except Exception as e:
      raise RuntimeError("An error occurred while fetching the dashboard data.") from e

    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
