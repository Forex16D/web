from flask import request, Blueprint, g

from application.container import container

model_routes = Blueprint("model_routes", __name__)
model_controller = ModelController(container.model_service)

@model_routes.route("/v1/models", methods=["POST"])
def get_models():
  return model_controller.login(request)

@model_routes.route("/v1/register", methods=["POST"])
def register():
  return model_controller.register(request)
