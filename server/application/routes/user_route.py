from flask import request, Blueprint, g
from application.services.middleware import token_required
from application.services.user import *
from application.container import container

from application.controllers.user_controller import UserController

user_routes = Blueprint("user_routes", __name__)

@user_routes.route("/v1/users", methods=["GET"])
@token_required
def users(current_user_id):
  user_controller = UserController(container.user_service)
  return user_controller.get_all_users(request)
