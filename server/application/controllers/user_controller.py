from flask import Flask, jsonify, request

class UserController:
  def __init__(self, portfolio_service): 
    self.portfolio_service = portfolio_service

  def get_all_users(self, request):
    try:
      users = self.portfolio_service.get_all_users(request)
      return jsonify(users), 200

    except RuntimeError:
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    except Exception:
      return jsonify({"status": 500, "message": "Internal server error"}), 500
