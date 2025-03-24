from psycopg2.extras import RealDictCursor # type: ignore
from application.helpers.logging import Logging

class UserService:
  def __init__(self, db_pool):
    self.db_pool = db_pool

  def get_all_users(self, request):
    limit = request.args.get("limit", default=10, type=int)
    page = request.args.get("page", default=1, type=int)

    offset = (page - 1) * limit
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM users LIMIT %s OFFSET %s", (limit, offset))
      users = cursor.fetchall()

      cursor.execute("SELECT COUNT(*) FROM users")
      total_users = cursor.fetchone()["count"]

      return {"users": users, "total_users": total_users}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def delete_user(self, current_user_id, user_id):
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
      conn.commit()

      cursor.close()
      Logging.admin_log(f"Admin {current_user_id} deleted user {user_id}")
      return {"message": "User Deleted Successfully!"}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      self.db_pool.release_connection(conn)

  def get_user_profile(self, user_id):
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
      profile = cursor.fetchone()

      return {"email": profile["email"],}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
      
  def ban_user(self, user_id):
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("UPDATE users SET is_banned = TRUE, is_expert = FALSE WHERE user_id = %s", (user_id,))
      conn.commit()

      return {"message": "User Banned Successfully!"}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def unban_user(self, user_id):
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("UPDATE users SET is_banned = FALSE WHERE user_id = %s", (user_id,))
      conn.commit()

      return {"message": "User Unbanned Successfully!"}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)

  def check_ban_status(self, user_id):
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT is_banned FROM users WHERE user_id = %s", (user_id,))
      status = cursor.fetchone()

      return status["is_banned"]
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)
      
  def check_ban_status_from_portfolio(self, portfolio_id):
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT is_banned FROM users WHERE user_id = (SELECT user_id FROM portfolios WHERE portfolio_id = %s)", (portfolio_id,))
      status = cursor.fetchone()

      return status["is_banned"]
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      cursor.close()
      self.db_pool.release_connection(conn)