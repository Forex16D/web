from flask import Flask, jsonify, request

class PortfolioController:
  def __init__(self, portfolio_service): 
    self.portfolio_service = portfolio_service

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

  def create_portfolio(self):
    data = request.get_json()
    if not data or not data.get('name'):
      return jsonify({"message": "Invalid data"}), 400
    portfolio = self.portfolio_service.create_portfolio(data)
    return jsonify(portfolio), 201

  def update_portfolio(self, portfolio_id):
    data = request.get_json()
    updated_portfolio = self.portfolio_service.update_portfolio(portfolio_id, data)
    if updated_portfolio:
      return jsonify(updated_portfolio), 200
    return jsonify({"message": "Portfolio not found"}), 404

  def delete_portfolio(self, portfolio_id):
    success = self.portfolio_service.delete_portfolio(portfolio_id)
    if success:
      return jsonify({"message": "Portfolio deleted successfully"}), 200
    return jsonify({"message": "Portfolio not found"}), 404
