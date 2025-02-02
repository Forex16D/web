from flask import request, Blueprint, g
from application.services.middleware import token_required
from application.services.portfolio_service import *
from application.controllers.portfolio_controller import PortfolioController


portfolio_routes = Blueprint("portfolio_routes", __name__)

@portfolio_routes.route("/v1/users/<user_id>/portfolios", methods=["GET"])
def get_portfolios(user_id):
  portfolio_controller = PortfolioController(g.portfolio_service)
  return portfolio_controller.get_portfolios(user_id)

@portfolio_routes.route("/v1/portfolios/<portfolio_id>", methods=["GET", "POST", "PUT", "DELETE"])
@token_required
def portfolio_by_id(current_user_id, portfolio_id):
  portfolio_controller = PortfolioController(g.portfolio_service)
  if request.method == "GET":
    return jsonify({"portfolio_id": portfolio_id, "data": "Portfolio data"}), 200
  elif request.method == "POST":
    return jsonify({"message": "Portfolio created"}), 201
  elif request.method == "PUT":
    return jsonify({"message": "Portfolio updated"}), 200
  elif request.method == "DELETE":
    return jsonify({"message": "Portfolio deleted"}), 200