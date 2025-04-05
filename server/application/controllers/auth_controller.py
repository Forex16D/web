from flask import jsonify  # type: ignore
from application.helpers.server_log_helper import ServerLogHelper
class AuthController:
  def __init__(self, auth_service): 
    self.auth_service = auth_service

  def login(self, request): 
    try:
      data = request.get_json()
      email = data.get("email").lower()
      password = data.get("password")
      remember = data.get("remember")

      token = self.auth_service.login(email, password, remember)
      return jsonify(token), 200
    except ValueError as e:
      if "Missing" in str(e):
        return jsonify({"status": 400, "message": "Bad request"}), 400
      else:
        return jsonify({"status": 401, "message": "Unauthorized"}), 401
      
    except RuntimeError as e:
      ServerLogHelper.error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    
    except Exception as e:
      ServerLogHelper.error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def register(self, request): 
    try:
      data = request.get_json()
      email = data.get("email").lower()
      password = data.get("password")
      confirm_password = data.get("confirmPassword")
  
      response = self.auth_service.register(email, password, confirm_password)
      return jsonify(response), 201

    except ValueError as e:
      if "Missing" in str(e):
        return jsonify({"status": 400, "message": "Bad request"}), 400
      elif "Email" in str(e):
        return jsonify({"status": 409, "message": "Conflict"}), 409
      else:
        return jsonify({"status": 401, "message": "Unauthorized"}), 401

    except RuntimeError as e:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

    except Exception as e:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def verify_user(self, request): 
    try:
      response = self.auth_service.verify_user(request)
      return jsonify(response), 200
    except ValueError as e:
      ServerLogHelper.error(e)
      return jsonify({"status": 401, "message": "Unauthorized"}), 401

    except RuntimeError as e:
      ServerLogHelper.error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500

    except Exception as e:
      ServerLogHelper.error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500