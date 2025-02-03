from flask import Flask, request, jsonify, g
from flask_cors import CORS
from psycopg2.extras import RealDictCursor


from application.routes.auth_route import auth_routes
from server.application.routes.user_route import user_routes
from application.routes.portfolio import portfolio_routes

from application.services.middleware import token_required

from application.container import AppContainer
from application.container import container

def create_app(container: AppContainer):
  app = Flask(__name__)
  CORS(app, resources={r"/*": {"origins": "*"}})

  @app.route("/")
  def check():
    return "Flask works!"

  @app.route("/v1/auth")
  @token_required
  def auth(current_user_id):
    return jsonify({"authentication": True}), 200

  app.register_blueprint(auth_routes)
  app.register_blueprint(user_routes)
  app.register_blueprint(portfolio_routes)
  
  @app.before_request
  def before_request():
    g.db_pool = container.db_pool
    g.hasher = container.hasher
    g.portfolio_service = container.portfolio_service
    g.auth_service = container.auth_service

  return app

app = create_app(container)

if __name__ == "__main__":
  app.run(debug=True)
