from psycopg2.extras import RealDictCursor # type: ignore

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

  def delete_user(self, user_id):
    conn = self.db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
      conn.commit()

      cursor.close()
      return {"message": "User Deleted Successfully!"}
    except Exception as e:
      raise RuntimeError(f"Something went wrong: {str(e)}")
    finally:
      self.db_pool.release_connection(conn)
