from flask import request, Blueprint # type: ignore

from application.container import container
from application.controllers.model_controller import ModelController
from application.services.middleware import admin_required

model_routes = Blueprint("model_routes", __name__)
model_controller = ModelController(container.model_service)

@model_routes.route("/v1/models", methods=["GET"])
@admin_required
def get_models(current_user_id):
  return model_controller.get_all_models(request)

@model_routes.route("/v1/models", methods=["POST"])
@admin_required
def create_models(current_user_id):

  return model_controller.create_models(request, current_user_id)

@model_routes.route("/v1/models/<model_id>", methods=["DELETE"])
@admin_required
def delete_model(current_user_id, model_id):
  return model_controller.delete_model(model_id, current_user_id)

@model_routes.route("/v1/models/<model_id>/train", methods=["POST"])
@admin_required
def train_model(current_user_id, model_id):
  return model_controller.train_model(model_id, request)

@model_routes.route("/v1/models/<model_id>/backtest", methods=["POST"])
@admin_required
def backtest_model(current_user_id, model_id):
  return model_controller.backtest_model(model_id)

@model_routes.route("/v1/models/<model_id>/evaluate/stop", methods=["POST"])
@admin_required
def stop_evaluate(current_user_id, model_id):
  return model_controller.stop_evaluate(model_id)

@model_routes.route("/v1/models/status", methods=["GET"])
@admin_required
def get_processes_status(current_user_id):
  return model_controller.get_processes_status()

@model_routes.route("/v1/models/<model_id>/status", methods=["GET"])
@admin_required
def get_process_status(current_user_id, model_id):
  return model_controller.get_process_status(model_id)

@model_routes.route("/v1/models/backtest/stream")
def stream_status():
  return model_controller.stream_backtest_status()

@model_routes.route("/v1/models/<model_id>", methods=["PUT"])
@admin_required
def update_model(current_user_id, model_id):
  return model_controller.update_model(request, model_id)
