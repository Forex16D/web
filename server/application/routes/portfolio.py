from flask import request, Blueprint, g
from application.services.middleware import token_required
from application.services.portfolio import *

portfolio_routes = Blueprint("portfolio_routes", __name__)

@portfolio_routes.route("/v1/portfolios/<user_id>", methods=["GET"])
def get_portfolios_by_user_route(user_id):
  return get_portfolios_by_user(g.db_pool, user_id)

@portfolio_routes.route("/v1/portfolios/<portfolio_id>", methods=["GET"])
@token_required
def get_portfolios_by_id_route(current_user_id):
  return 200