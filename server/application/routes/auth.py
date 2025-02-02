from flask import request, Blueprint, g

from application.services.auth import *

auth_routes = Blueprint("auth_routes", __name__)

@auth_routes.route("/v1/login", methods=["POST"])
def login_route():
  return login(request, g.db_pool, g.hasher)

@auth_routes.route("/v1/register", methods=["POST"])
def register_route():
  return register(request, g.db_pool, g.hasher)
