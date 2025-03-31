from flask import Flask, jsonify, request # type: ignore
from application.helpers.server_log_helper import ServerLogHelper

class PortfolioController:
  def __init__(self, portfolio_service): 
    self.portfolio_service = portfolio_service
    self.server_log_service = ServerLogHelper

  def get_portfolios(self, user_id):
    try:
      portfolios = self.portfolio_service.get_portfolios_by_user(user_id)
      return jsonify(portfolios), 200
    except Exception:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def get_portfolio(self, portfolio_id):
    try:
      portfolio = self.portfolio_service.get_portfolio_by_id(portfolio_id)
      if portfolio:
        return jsonify(portfolio), 200
      return jsonify({"status": 404, "message": "Not found"}), 404
    except Exception:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def get_expert_portfolios(self):
    try:
      portfolios = self.portfolio_service.get_expert_portfolios()
      return portfolios
    except Exception as e:
      self.server_log_service.error(f"Internal server error during expert portfolio retrieval: {str(e)}")
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def get_portfolio_commission(self, portfolio_id):
    try:
      commissions = self.portfolio_service.get_portfolio_commission(portfolio_id)
      return commissions
    except Exception as e:
      self.server_log_service.error(f"Internal server error during portfolio commission retrieval: {str(e)}")
      return jsonify({"status": 500, "message": "Internal server error"}), 500
  
  def get_total_commission(self, user_id):
    try:
      commissions = self.portfolio_service.get_total_commission(user_id)
      return commissions
    except Exception as e:
      self.server_log_service.error(f"Internal server error during portfolio commission retrieval: {str(e)}")
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def get_user_balance(self, user_id):
    try:
      commissions = self.portfolio_service.get_user_balance(user_id)
      return commissions
    except Exception as e:
      self.server_log_service.error(f"Internal server error during user balance retrieval: {str(e)}")
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def create_portfolio(self, request, user_id):
    try:
      data = request.get_json()
      portfolio = self.portfolio_service.create_portfolio(data, user_id)
      return jsonify(portfolio), 201
    except ValueError:
      return jsonify({"status": 400, "message": "Bad request"}), 400
    except RuntimeError as re:
      self.server_log_service.error(f"Internal server error during portfolio creation: {str(re)}")
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    except Exception as e:
      self.server_log_service.error(f"Unexpected error during portfolio creation: {str(e)}")
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def update_portfolio(self, request, portfolio_id):
    try:
      data = request.get_json()
      updated_portfolio = self.portfolio_service.update_portfolio(data, portfolio_id)
      if updated_portfolio:
        return jsonify(updated_portfolio), 200
      return jsonify({"status": 404, "message": "Not found"}), 404
    except ValueError:
      return jsonify({"status": 400, "message": "Bad request"}), 400
    except Exception:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def delete_portfolio(self, portfolio_id, user_id):
    try:
      success = self.portfolio_service.delete_portfolio(portfolio_id, user_id)
      if success:
        return jsonify({"message": "Portfolio deleted successfully"}), 200
      return jsonify({"status": 404, "message": "Not found"}), 404
    except Exception:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def copy_trade(self, request, expert_id, user_id):
    try:
      data = request.get_json()
      portfolio_id = data.get("portfolio_id")

      response = self.portfolio_service.copy_trade(portfolio_id, expert_id, user_id)
      return jsonify(response), 200
    except ValueError as e:
      ServerLogHelper.error(str(e))
      return {"status": 400, "message": "Bad Request"}, 400
    except Exception as e:
      ServerLogHelper.error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500      
