from flask import jsonify  # type: ignore
from application.helpers.server_log_helper import ServerLogHelper
from application.helpers.logging import Logging

class ModelController:
  def __init__(self, model_service): 
    self.model_service = model_service

  def get_all_models(self, request): 
    try:
      response = self.model_service.get_all_models(request)
      return jsonify(response), 200
    except:
      return {"status": 500, "message": "Internal server error"}, 500
  
  def create_models(self, request, current_user_id):
    try:
      files = request.files.getlist('files[]')
      if not files:
        return {"status": 400, "message": "Bad Request"}, 400

      response = self.model_service.create_models(files)

      Logging.admin_log(f"User {current_user_id} created model {response['model_id']}")
      return jsonify(response), 201

    except ValueError as e:
      return {"status": 400, "message": "Bad Request"}, 400
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500

  def delete_model(self, model_id, current_user_id): 
    try:
      response = self.model_service.delete_model(model_id)

      Logging.admin_log(f"User {current_user_id} deleted model {model_id}")
      return jsonify(response), 200

    except ValueError as e:
      return {"status": 400, "message": "Bad Request"}, 400
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500
