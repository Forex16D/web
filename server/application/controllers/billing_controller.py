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
      ServerLogHelper.error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500
    
  def get_bill(self, user_id, bill_id):
    try:
      response = self.billing_service.get_bill(user_id, bill_id)
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper.error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500
  
  def get_orders(self, bill_id):
    try:
      response = self.billing_service.get_orders(bill_id)
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper.error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500

  def pay_bill(self, user_id, request):
    try:
      bill_id = request.form.get("bill_id")
      notes = request.form.get("notes")
      method = request.form.get("method")
      
      receipt_image = None
      
      # Log the incoming request for debugging
      ServerLogHelper.log(f"Request Method: {method} for bill_id: {bill_id}")

      if method == 'receipt':
        receipt_image = request.files.get("receipt")
        if not receipt_image:
          ServerLogHelper.log("No receipt image found, returning 400")
          return jsonify({"status": 400, "message": "Bad Request"}), 400
        response = self.billing_service.pay_bill(user_id, bill_id, receipt_image, notes)
      elif method == 'wallet':
        response = self.billing_service.pay_bill_wallet(user_id, bill_id, notes)
        ServerLogHelper.log(f"{response}")

      else:
        return jsonify({"status": 400, "message": "Bad Request"}), 400
      
      return jsonify(response), 200

    except ValueError as e:
      return jsonify({"status": 400, "message": "Bad Request", "error": str(e)}), 400
    except Exception as e:
      ServerLogHelper.log(f"General Exception Triggered: {str(e)}")  # Debug log for general exceptions
      return jsonify({"status": 500, "message": f"Internal server error: {str(e)}"}), 500

  def get_withdraw_requests_admin(self):
    try:
      response = self.billing_service.get_withdraw_requests_admin()
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper.error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500   

  def create_withdraw_request(self, user_id, request):
    try:
      data = request.get_json()
      amount = data.get("amount")
      method = data.get("method")
      bank_account = data.get("bankAccount")
      wallet_address = data.get("walletAddress")

      response = self.billing_service.create_withdraw_request(user_id, amount, method, bank_account, wallet_address)

      return jsonify(response), 200
    except ValueError as e:
      return jsonify({"status": 400, "message": str(e)}), 400
    except Exception as e:
      ServerLogHelper.log(f"General Exception Triggered: {str(e)}")  # Debug log for general exceptions
      return jsonify({"status": 500, "message": f"Internal server error: {str(e)}"}), 500

  def update_withdraw_request_status(self, user_id, withdraw_id, action):
    try:
      response = self.billing_service.update_withdraw_request_status(withdraw_id, action)
      return jsonify(response), 200
    except ValueError as e:
      return jsonify({"status": 400, "message": f"Bad Request {str(e)}"}), 400
    except Exception as e:
      ServerLogHelper.log(f"General Exception Triggered: {str(e)}")  # Debug log for general exceptions
      return jsonify({"status": 500, "message": f"Internal server error: {str(e)}"}), 500

