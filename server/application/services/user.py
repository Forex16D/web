from flask import jsonify
from psycopg2.extras import RealDictCursor

def get_all_users(request, db_pool):
    limit = request.args.get("limit", default=10, type=int)
    page = request.args.get("page", default=1, type=int)

    offset = (page - 1) * limit
    conn = db_pool.get_connection()

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM users LIMIT %s OFFSET %s", (limit, offset))
      users = cursor.fetchall()

      cursor.execute("SELECT COUNT(*) FROM users")
      total_users = cursor.fetchone()["count"]

      cursor.close()
      return jsonify({"users": users, "total_users": total_users}), 200
    except Exception as e:
      return jsonify({"message": "Something went wrong"}), 500
    finally:
      db_pool.release_connection(conn)