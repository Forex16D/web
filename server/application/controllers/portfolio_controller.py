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
    except ValueError:
      return jsonify({"status": 404, "message": "Not found"}), 404
    except RuntimeError:
      return jsonify({"status": 500, "message": "Internal server error"}), 500
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

  def create_portfolio(self, request, user_id):
    try:
      data = request.get_json()
      portfolio = self.portfolio_service.create_portfolio(data, user_id)
      return jsonify(portfolio), 201
    except ValueError:
      return jsonify({"status": 400, "message": "Bad request"}), 400
    except RuntimeError:
      self.server_log_service.log_error("Internal server error during portfolio creation")
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    except Exception:
      self.server_log_service.log_error("Unexpected error during portfolio creation")
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
