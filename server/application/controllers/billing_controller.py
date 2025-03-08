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
    

  def pay_bill(self, user_id, request):
    try:
      bill_id = request.form.get("bill_id")
      payment_method = request.form.get("payment_method")
      reference_number = request.form.get("reference_number")
      payment_date = request.form.get("payment_date")
      notes = request.form.get("notes")

      receipt_image = request.files.get("receipt")

      if not bill_id or not receipt_image:
        return jsonify({"status": 100, "message": "Missing required fields"}), 400

      image_path = f"uploads/{receipt_image.filename}"
      receipt_image.save(image_path)
      
      response = self.billing_service.pay_bill(user_id, bill_id, image_path, payment_method, reference_number, payment_date, notes)
      
      return jsonify(response), 200

    except Exception as e:
      return jsonify({"status": 500, "message": f"Internal server error: {str(e)}"}), 500
