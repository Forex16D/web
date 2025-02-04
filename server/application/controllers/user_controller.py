from flask import Flask, jsonify, request

class UserController:
  def __init__(self, portfolio_service): 
    self.portfolio_service = portfolio_service

  def get_all_users(self, request):
    try:
      users = self.portfolio_service.get_all_users(request)
      return jsonify(users), 200

    except RuntimeError as re:
      return jsonify({"status": 500, "message": f"Internal server error: {str(re)}"}), 500
    except Exception as e:
      return jsonify({"message": "An unexpected error occurred"}), 500
