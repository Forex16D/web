import threading

from flask import Flask, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore

from application.routes.auth_route import auth_routes
from application.routes.user_route import user_routes
from application.routes.portfolio_route import portfolio_routes
from application.routes.mt_route import mt_routes
from application.routes.model_route import model_routes
from application.routes.market_data_route import market_data_routes

from application.services.middleware import token_required
from application.helpers.server_log_helper import ServerLogHelper

shutdown_event = threading.Event()

def create_app():
  app = Flask(__name__)
  CORS(app, resources={r"/*": {"origins": "*"}})

  @app.route("/")
  def check():
    return "Flask works!"

  app.register_blueprint(auth_routes)
  app.register_blueprint(user_routes)
  app.register_blueprint(portfolio_routes)
  app.register_blueprint(mt_routes)
  app.register_blueprint(model_routes)
  app.register_blueprint(market_data_routes)
  
  return app

app = create_app()

if __name__ == "__main__":
  app.run(debug=True)
