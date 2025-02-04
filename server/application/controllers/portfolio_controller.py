from flask import Flask, jsonify, request
from application.helpers.server_log_service import ServerLogService

class PortfolioController:
  def __init__(self, portfolio_service): 
    self.portfolio_service = portfolio_service
    self.server_log_service = ServerLogService()

  def get_portfolios(self, user_id):
    try:
      portfolios = self.portfolio_service.get_portfolios_by_user(user_id)
      return jsonify(portfolios), 200
    except ValueError as ve:
      return jsonify({"status": 404, "message": str(ve)}), 404
    except RuntimeError as re:
      return jsonify({"status": 500, "message": f"Internal server error: {str(re)}"}), 500
    except Exception as e:
      return jsonify({"message": "An unexpected error occurred"}), 500

  def get_portfolio(self, portfolio_id):
    portfolio = self.portfolio_service.get_portfolio_by_id(portfolio_id)
    if portfolio:
      return jsonify(portfolio), 200
    return jsonify({"message": "Portfolio not found"}), 404

  def create_portfolio(self, request, user_id):
    try:
      data = request.get_json()
      portfolio = self.portfolio_service.create_portfolio(data, user_id)
      return jsonify(portfolio), 201
    except ValueError as ve:
      return jsonify({"status": 400, "message": str(ve)}), 400
    except RuntimeError as re:
      self.server_log_service.log_error(re)
      return jsonify({"status": 500, "message": f"Internal server error: {str(re)}"}), 500
    except Exception as e:
      self.server_log_service.log_error(e)
      return jsonify({"message": "An unexpected error occurred"}), 500

  def update_portfolio(self, request, portfolio_id):
    data = request.get_json()
    updated_portfolio = self.portfolio_service.update_portfolio(data, portfolio_id)
    if updated_portfolio:
      return jsonify(updated_portfolio), 200
    return jsonify({"message": "Portfolio not found"}), 404

  def delete_portfolio(self, portfolio_id, user_id):
    success = self.portfolio_service.delete_portfolio(portfolio_id, user_id)
    if success:
      return jsonify({"message": "Portfolio deleted successfully"}), 200
    return jsonify({"message": "Portfolio not found"}), 404
