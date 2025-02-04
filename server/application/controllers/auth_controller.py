from flask import jsonify

class AuthController:
  def __init__(self, auth_service): 
    self.auth_service = auth_service

  def login(self, request): 
    try:
      data = request.get_json()
      if not data:
        raise ValueError("Invalid request body, data is missing.")

      token = self.auth_service.login(data)
      return jsonify(token), 200
    except ValueError as ve:
      return jsonify({"status": 401, "message": str(ve)}), 401
    except RuntimeError as re:
      return jsonify({"status": 500, "message": f"Internal server error: {str(re)}"}), 500
    except Exception as e:
      return jsonify({"message": "An unexpected error occurred"}), 500

  def register(self, request): 
    try:
      data = request.get_json()
      if not data:
        raise ValueError("Invalid request body, data is missing.")

      response = self.auth_service.register(data)
      return jsonify(response), 201

    except ValueError as ve:
      return jsonify({"status": 400, "message": str(ve)}), 400

    except RuntimeError as re:
      return jsonify({"status": 500, "message": f"Internal server error: {str(re)}"}), 500

    except Exception as e:
      return jsonify({"status": 500, "message": "An unexpected error occurred"}), 500
