from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from argon2 import PasswordHasher

from application.routes.login import login
from application.routes.register import register

from application.services.middleware import token_required
from application.services.db import DatabasePool

class AppContainer:
  def __init__(self):
    self.db_pool = DatabasePool()
    self.hasher = PasswordHasher()
        
def create_app(container: AppContainer):
  app = Flask(__name__)
  CORS(app, resources={r"/*": {"origins": "*"}}) 

  @app.route("/")
  def hello_world():
    return "<p>Hello, World!</p>"

  @app.route("/v1/login", methods=['POST'])
  def handle_login():
    return login(request, container.db_pool)
  
  @app.route("/v1/register", methods=['POST'])
  def handle_register():
    return register(request, container.db_pool, container.hasher)

  @app.route("/v1/protected", methods=['GET'])
  @token_required
  def protected_route(current_user):
    return jsonify({"message": f"Hello {current_user}, this is a protected route!"})

  @app.route("/v1/users", methods=['GET'])
  def get_users():
    conn = container.db_pool.get_connection()
    limit = request.args.get("limit", default=10, type=int)
    page = request.args.get("page", default=1, type=int)

    offset = (page - 1) * limit

    try:
      cursor = conn.cursor(cursor_factory=RealDictCursor)
      cursor.execute("SELECT * FROM users LIMIT %s OFFSET %s", (limit, offset))
      users = cursor.fetchall()

      cursor.execute("SELECT COUNT(*) FROM users")
      total_users = cursor.fetchone()["count"]

      cursor.close()
      return jsonify({"users": users, "total_users": total_users}), 200
    except Exception as e:
      print(e)
      return jsonify({"error": str(e)}), 500
    finally:
      container.db_pool.release_connection(conn)

  return app

container = AppContainer()
app = create_app(container)

if __name__ == "__main__":
  app.run(debug=True)
