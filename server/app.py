from flask import Flask, jsonify
from flask_cors import CORS


from application.routes.auth_route import auth_routes
from application.routes.user_route import user_routes
from application.routes.portfolio_route import portfolio_routes

from application.services.middleware import token_required

def create_app():
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

  return app

app = create_app()

if __name__ == "__main__":
  app.run(debug=True)
