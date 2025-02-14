from flask import request, Blueprint, g

from application.controllers.auth_controller import AuthController
from application.container import container

auth_routes = Blueprint("auth_routes", __name__)
auth_controller = AuthController(container.auth_service)

@auth_routes.route("/v1/login", methods=["POST"])
def login():
  return auth_controller.login(request)

@auth_routes.route("/v1/register", methods=["POST"])
def register():
  return auth_controller.register(request)

@auth_routes.route("/v1/auth", methods=["GET"])
def verify_user():
  return auth_controller.verify_user(request)
