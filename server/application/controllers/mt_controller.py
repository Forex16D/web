from flask import jsonify # type: ignore
from application.helpers.server_log_helper import ServerLogService

class MtController:
  def __init__(self, mt_service):
    self.mt_service = mt_service
    self.server_log_service = ServerLogService()

  def verify_token(self, request):
    try:
      response = self.mt_service.verify_token(request)
      return jsonify(response), 200

    except ValueError as ve:
      self.server_log_service.error(ve)
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    except RuntimeError as re:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

    except Exception as e:
      self.server_log_service.error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500

      