from flask import jsonify  # type: ignore
from application.helpers.server_log_helper import ServerLogService

class ModelController:
  def __init__(self, model_service): 
    self.model_service = model_service

  def get_all_models(self, request): 
    try:
      data = request.get_json()
      token = self.model_service.login(data)
      return jsonify(token), 200

    except RuntimeError as e:
      ServerLogService().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
    
    except Exception as e:
      ServerLogService().error(e)
      return jsonify({"status": 500, "message": "Internal server error"}), 500
 
  def create_models(self, request, current_user_id): 
    if not request.files:
      return {"status": 400, "message": "Bad Request"}, 400
   
    try:
      form_data = request.form
      files = request.files.getlist('files[]')
      ServerLogService().log(files)
      response = self.model_service.create_models(form_data, files)
      return jsonify(response), 201

    except ValueError as e:
      return {"status": 400, "message": "Bad Request"}, 400
    except Exception as e:
      ServerLogService().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500
