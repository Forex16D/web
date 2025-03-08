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
        "totalUsers": dashboard_data["user_count"],
        "totalModels": dashboard_data["model_count"],
        "totalRevenue": dashboard_data["revenue"],
        "activeSubscriptions": dashboard_data["subscriptions"]
      }
    
    except ValueError as ve:
      raise ve
    
    except Exception as e:
      raise RuntimeError("An error occurred while fetching the dashboard data.") from e

    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
