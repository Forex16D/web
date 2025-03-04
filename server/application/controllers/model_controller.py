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

      # Logging.admin_log(f"User {current_user_id} created model {response['model_id']}")
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
  
  def update_model(self, request, model_id):
    try:
      response = self.model_service.update_model(request, model_id)
      return jsonify(response), 200
    except ValueError as e:
      ServerLogHelper().error(str(e))
      return {"status": 400, "message": "Bad Request"}, 400
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500
    
    
  def train_model(self, model_id, request): 
    try:
      data = request.get_json()
      start_date = data.get("start_date")
      bars = data.get("bars")
      response = self.model_service.train_model(model_id, start_date, bars)
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500
    
  def backtest_model(self, model_id): 
    try:
      response = self.model_service.backtest_model(model_id)
      return jsonify(response), 200
    except ValueError as e:
      return {"status": 400, "message": "Bad Request"}, 400
    except Exception as e:
      ServerLogHelper().error(e)
      return {"status": 500, "message": "Internal server error"}, 500
    
  def stop_backtest(self, model_id): 
    try:
      response = self.model_service.stop_backtest()
      return jsonify(response), 200
    except ValueError as e:
      return {"status": 400, "message": "Bad Request"}, 400
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500

  def get_process_status(self, model_id): 
    try:
      response = self.model_service.get_process_status()
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500

  def get_processes_status(self): 
    try:
      response = self.model_service.get_processes_status()
      return jsonify(response), 200
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500

  def stream_backtest_status(self): 
    try:
      response = self.model_service.stream_backtest_status()
      return response, 200
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500