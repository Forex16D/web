from flask import jsonify

class AuthController:
  def __init__(self, auth_service): 
    self.auth_service = auth_service

  def login(self, request): 
    try:
      data = request.get_json()
      token = self.auth_service.login(data)
      return jsonify(token), 200
    except ValueError as ve:
      if "Missing" in str(ve):
        return jsonify({"status": 400, "message": "Bad request"}), 400
      else:
        return jsonify({"status": 401, "message": "Unauthorized"}), 401
      
    except RuntimeError:
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    
    except Exception:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

  def register(self, request): 
    try:
      data = request.get_json()
      response = self.auth_service.register(data)
      return jsonify(response), 201

    except ValueError as ve:
      if "Missing" in str(ve):
        return jsonify({"status": 400, "message": "Bad request"}), 400
      elif "Email" in str(ve):
        return jsonify({"status": 409, "message": "Conflict"}), 409
      else:
        return jsonify({"status": 401, "message": "Unauthorized"}), 401

    except RuntimeError as re:
      return jsonify({"status": 500, "message": "Internal server error"}), 500

    except Exception as e:
      return jsonify({"status": 500, "message": "Internal server error"}), 500
