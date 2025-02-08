import threading
import signal
from flask import Flask, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore

from application.routes.auth_route import auth_routes
from application.routes.user_route import user_routes
from application.routes.portfolio_route import portfolio_routes
from application.routes.mt_route import mt_routes

from application.services.middleware import token_required
from application.services.zmq_service import ZeroMQService  # Assuming the ZeroMQService class is defined here
from application.helpers.server_log_helper import ServerLogService

shutdown_event = threading.Event()

def create_app():
  app = Flask(__name__)
  CORS(app, resources={r"/*": {"origins": "*"}})

  zmq_service = ZeroMQService()

  sender_thread = threading.Thread(target=zmq_service.start_zmq)  # Don't use daemon=True
  sender_thread.start()

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
  app.register_blueprint(mt_routes)

  def cleanup(exception=None):
    ServerLogService().log("Cleaning up threads and shutting down ZeroMQ.")
    zmq_service.cleanup()
    shutdown_event.set()
    sender_thread.join() 

  signal.signal(signal.SIGTERM, lambda signum, frame: cleanup())
  signal.signal(signal.SIGINT, lambda signum, frame: cleanup())

  app.teardown_appcontext(cleanup)
  return app

app = create_app()

if __name__ == "__main__":
  app.run(debug=True)
