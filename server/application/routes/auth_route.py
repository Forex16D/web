from flask import request, Blueprint, g

from application.services.auth import *

from application.controllers.auth_controller import AuthController
from application.container import container

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/v1/login", methods=["POST"])
def login_route():
  auth_controller = AuthController(container.auth_service)
  return auth_controller.login(request)

@auth_routes.route("/v1/register", methods=["POST"])
def register_route():
  auth_controller = AuthController(container.auth_service)
  return auth_controller.register(request)
