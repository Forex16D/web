from flask import jsonify # type: ignore
from application.helpers.server_log_helper import ServerLogHelper

class AdminController:
  def __init__(self, admin_service):
    self.admin_service = admin_service
  
  def get_dashboard(self):
    try:
      response = self.admin_service.get_dashboard()
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper.error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500
  
  def get_revenue(self):
    try:
      response = self.admin_service.get_revenue()
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper.error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500

  def get_model_usage(self):
    try:
      response = self.admin_service.get_model_usage()
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper.error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500