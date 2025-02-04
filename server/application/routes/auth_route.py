from flask import request, Blueprint, g

from application.controllers.auth_controller import AuthController
from application.container import container

auth_routes = Blueprint("auth_routes", __name__)
auth_controller = AuthController(container.auth_service)

@auth_routes.route("/v1/login", methods=["POST"])
def login_route():
  return auth_controller.login(request)

@auth_routes.route("/v1/register", methods=["POST"])
def register_route():
  return auth_controller.register(request)
