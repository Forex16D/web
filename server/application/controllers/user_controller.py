from flask import Flask, jsonify, request # type: ignore
from application.helpers.server_log_helper import ServerLogHelper

class UserController:
  def __init__(self, user_service): 
    self.user_service = user_service

  def get_all_users(self, request):
    try:
      users = self.user_service.get_all_users(request)
      return jsonify(users), 200

    except RuntimeError as e:
      ServerLogHelper().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    except Exception as e:
      ServerLogHelper().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def delete_user(self, current_user_id, user_id):
    try:
      if current_user_id != user_id:
        users = self.user_service.delete_user(current_user_id, user_id)
        return jsonify(users), 200
      else:
        ServerLogHelper().error(f"{user_id} {current_user_id}")
        return jsonify({"status": 418, "message": "I'm a teapot"}), 418
      
    except RuntimeError as e:
      ServerLogHelper().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    except Exception:
      ServerLogHelper().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    
  def get_user_profile(self, current_user_id):
    try:
      profile = self.user_service.get_user_profile(current_user_id)
      return jsonify(profile), 200

    except RuntimeError as e:
      ServerLogHelper().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    except Exception:
      ServerLogHelper().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500