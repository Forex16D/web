from flask import request, Blueprint # type: ignore

from application.controllers.billing_controller import BillingController
from application.container import container
from application.services.middleware import  token_required, admin_required
bill_routes = Blueprint("bill_routes", __name__)
bill_controller = BillingController(container.billing_service)

@bill_routes.route("/v1/bills", methods=["GET"])
@token_required
def get_bills(current_user_id):
  return bill_controller.get_bills(current_user_id)

@bill_routes.route("/v1/bills/<bill_id>", methods=["GET"])
@token_required
def get_bill(current_user_id, bill_id):
  return bill_controller.get_bill(current_user_id, bill_id)

@bill_routes.route("/v1/payments", methods=["POST"])
@token_required
def pay_bill(current_user_id):
  return bill_controller.pay_bill(current_user_id, request)

@bill_routes.route("/v1/withdrawals", methods=["POST"])
@token_required
def create_withdraw_request(current_user_id):
  return bill_controller.create_withdraw_request(current_user_id, request)

@bill_routes.route("/v1/withdrawals/<withdraw_id>/<action>", methods=["PUT"])
@admin_required
def update_withdraw_request_status(current_user_id, withdraw_id, action):
  return bill_controller.update_withdraw_request_status(current_user_id, withdraw_id, action)

@bill_routes.route("/v1/withdrawals/admin", methods=["GET"])

def get_withdraw_requests_admin():
  return bill_controller.get_withdraw_requests_admin()