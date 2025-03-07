from flask import request, Blueprint, g

from application.controllers.billing_controller import BillingController
from application.container import container
from application.services.middleware import  token_required
bill_routes = Blueprint("bill_routes", __name__)
bill_controller = BillingController(container.billing_service)

@bill_routes.route("/v1/bills", methods=["get"])
@token_required
def get_bills(current_user_id):
  return bill_controller.get_bills(current_user_id)

@bill_routes.route("/v1/bills/<bill_id>", methods=["get"])
@token_required
def get_bill(current_user_id, bill_id):
  return bill_controller.get_bill(current_user_id, bill_id)


