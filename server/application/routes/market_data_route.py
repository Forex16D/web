from flask import request, Blueprint # type: ignore

from application.container import container
from application.controllers.market_data_controller import MarketDataController
from application.services.middleware import admin_required

market_data_routes = Blueprint("market_data_routes", __name__)
market_data_controller = MarketDataController(container.market_data_service)

@market_data_routes.route("/v1/market-data", methods=["POST"])
def import_from_csv():
  return market_data_controller.import_from_csv(request)

