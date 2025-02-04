from flask import request, Blueprint, jsonify
from application.services.middleware import token_required
from application.controllers.portfolio_controller import PortfolioController
from application.container import container

portfolio_routes = Blueprint("portfolio_routes", __name__)

portfolio_controller = PortfolioController(container.portfolio_service)

@portfolio_routes.route("/v1/portfolios", methods=["GET"])
@token_required
def get_portfolios(current_user_id):
  return portfolio_controller.get_portfolios(current_user_id)

@portfolio_routes.route("/v1/portfolios", methods=["POST"])
@token_required
def create_portfolio(current_user_id):
  return portfolio_controller.create_portfolio(request, current_user_id)

@portfolio_routes.route("/v1/portfolios/<portfolio_id>", methods=["GET", "PUT", "DELETE"])
@token_required
def portfolio_by_id(current_user_id, portfolio_id):
  if request.method == "GET":
    return portfolio_controller.get_portfolio(portfolio_id, current_user_id)
  elif request.method == "PUT":
    return portfolio_controller.update_portfolio(request, portfolio_id)
  elif request.method == "DELETE":
    return portfolio_controller.delete_portfolio(portfolio_id, current_user_id)
  return jsonify({"error": "Method not allowed"}), 405
