from flask import Flask, request, jsonify
from flask_cors import CORS 
from psycopg2.extras import RealDictCursor
import psycopg2

from application.routes.login import login
from application.services.middleware import token_required
from application.services.db import DatabasePool

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

db_pool = DatabasePool()

@app.route("/")
def hello_world():
  return "<p>Hello, World!</p>"

@app.route("/v1/login", methods=['POST'])
def handle_login():
  return login(request, db_pool)

@app.route("/v1/protected", methods=['GET'])
@token_required
def protected_route(current_user):
  return jsonify({"message": f"Hello {current_user}, this is a protected route!"})

@app.route("/v1/users", methods=['GET'])
def get_users():
  conn = db_pool.get_connection()
  limit = request.args.get("limit", default=10, type=int)
  page = request.args.get("page", default=1, type=int)
  
  offset = (page - 1) * limit

  try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users")
    user = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()["count"]

    cursor.close()

    return jsonify({"users": user, "total_users": total_users}), 200
  except Exception as e:
    print(e)
    return jsonify({"error": str(e)}), 500
  finally:
    db_pool.release_connection(conn)

if __name__ == "__main__":
  app.run(debug=True)
