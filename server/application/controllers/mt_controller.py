from flask import jsonify # type: ignore
from application.helpers.server_log_helper import ServerLogHelper

class MtController:
  def __init__(self, mt_service):
    self.mt_service = mt_service
    self.server_log_service = ServerLogHelper

  def verify_token(self, request):
    try:
      response = self.mt_service.verify_token(request)
      return jsonify(response), 200

    except ValueError as e:
      if str(e) == "User has unpaid bills":
        self.server_log_service.error(f"Unpaid bill error: {e}")
        return jsonify({"status": 403, "message": "Forbidden"}), 403
      
      self.server_log_service.error(e)
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    except RuntimeError as e:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

    except Exception as e:
      self.server_log_service.error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500


  def create_order(self, request):
    try:
      response = self.mt_service.create_order(request)
      return jsonify(response), 201

    except ValueError as e:
      self.server_log_service.error(e)
      return jsonify({"status": 400, "message": "Bad request"}), 400

    except RuntimeError as e:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

    except Exception as e:
      self.server_log_service.error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500