from flask import request, Blueprint # type: ignore

from application.container import container
from application.controllers.model_controller import ModelController
from application.services.middleware import admin_required

model_routes = Blueprint("model_routes", __name__)
model_controller = ModelController(container.model_service)

@model_routes.route("/v1/models", methods=["GET"])
# @admin_required
def get_models():
  return model_controller.get_all_models(request)

@model_routes.route("/v1/models", methods=["POST"])
@admin_required
def create_models(current_user_id):
  # if request.content_type != "multipart/form-data":
  # return {"status": 415, "message": request.content_type}, 415
  return model_controller.create_models(request, current_user_id)

@model_routes.route("/v1/models/<model_id>", methods=["DELETE"])
@admin_required
def delete_model(current_user_id, model_id):
  return model_controller.delete_model(model_id, current_user_id)

