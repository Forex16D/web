from flask import jsonify # type: ignore
from application.helpers.server_log_helper import ServerLogHelper

class BillingController:
  def __init__(self, billing_service):
    self.billing_service = billing_service
    
  def get_bills(self, user_id):
    try:
      response = self.billing_service.get_bills(user_id)
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500
    
  def get_bill(self, user_id, bill_id):
    try:
      response = self.billing_service.get_bill(user_id, bill_id)
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500