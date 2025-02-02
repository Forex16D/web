from flask import jsonify
from psycopg2.extras import RealDictCursor
import jwt

def get_portfolios_by_user(db_pool, user_id):
  conn = db_pool.get_connection()

  try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM portfolios WHERE user_id = %s", (user_id,))
    portfolios = cursor.fetchall()

    cursor.close()
    return jsonify({"portfolios": portfolios}), 200
  except Exception as e:
    return jsonify({"message": "Something went wrong"}), 500
  finally:
    db_pool.release_connection(conn)

def manage_portfolio(portfolio_id, current_user):
  pass