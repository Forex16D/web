from flask import Flask, jsonify, request # type: ignore
from application.helpers.server_log_helper import ServerLogService

class UserController:
  def __init__(self, user_service): 
    self.portfolio_service = user_service

  def get_all_users(self, request):
    try:
      users = self.portfolio_service.get_all_users(request)
      return jsonify(users), 200

    except RuntimeError as e:
      ServerLogService().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    except Exception as e:
      ServerLogService().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def delete_user(self, current_user_id, user_id):
    try:
      # if current_user_id == user_id:
      #   users = self.portfolio_service.delete_user(user_id)
      #   return jsonify(users), 200
      # else:
      
      ServerLogService().error(f"{user_id} {current_user_id}")
      return jsonify({"status": 418, "message": "I'm a teapot"}), 418
      
    except RuntimeError as e:
      ServerLogService().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    except Exception:
      ServerLogService().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500