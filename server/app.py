import os
import threading
from flask import Flask, jsonify, send_file # type: ignore
from flask_cors import CORS  # type: ignore
from application.services.task_scheduler import run_scheduler

from application.routes.auth_route import auth_routes
from application.routes.user_route import user_routes
from application.routes.portfolio_route import portfolio_routes
from application.routes.mt_route import mt_routes
from application.routes.model_route import model_routes
from application.routes.market_data_route import market_data_routes
from application.routes.billing_route import bill_routes
from application.routes.admin_route import admin_routes

from application.services.middleware import token_required
from application.helpers.server_log_helper import ServerLogHelper

shutdown_event = threading.Event()

def create_app():
  app = Flask(__name__)
  
  UPLOAD_FOLDER = "resources"
  app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

  CORS(app, resources={r"/*": {"origins": "*"}})

  @app.route("/")
  def check():
    return "Flask works!"

  @app.route("/download/<filename>", methods=["GET"])
  def download_file(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

  app.register_blueprint(auth_routes)
  app.register_blueprint(user_routes)
  app.register_blueprint(portfolio_routes)
  app.register_blueprint(mt_routes)
  app.register_blueprint(model_routes)
  app.register_blueprint(market_data_routes)
  app.register_blueprint(bill_routes)
  app.register_blueprint(admin_routes)
  
  return app

app = create_app()

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
  app.run(debug=True)
