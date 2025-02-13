from flask import request, Blueprint, jsonify #type: ignore
from application.controllers.mt_controller import MtController
from application.container import container

mt_routes = Blueprint("mt_routes", __name__)
mt_controller = MtController(container.mt_service)

@mt_routes.route("/v1/mt/auth", methods=["GET"])
def verify_token():
  return mt_controller.verify_token(request)
