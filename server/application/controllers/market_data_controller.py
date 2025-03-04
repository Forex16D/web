from flask import jsonify # type: ignore
from application.helpers.server_log_helper import ServerLogHelper

class MarketDataController:
  def __init__(self, market_data_service):
    self.market_data_service = market_data_service
    
  def import_from_csv(self, request):
    try:
      file_path = request.get_json().get("file_path")
      response = self.market_data_service.import_from_csv(file_path)
      return jsonify({"message": "hello"}), 200
    except Exception as e:
      ServerLogHelper().error(str(e))
      return {"status": 500, "message": "Internal server error"}, 500