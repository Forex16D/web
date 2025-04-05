from flask import request, Blueprint # type: ignore
from flasgger import swag_from

from application.controllers.admin_controller import AdminController
from application.container import container
from application.services.middleware import admin_required

admin_routes = Blueprint("admin_routes", __name__)
admin_controller = AdminController(container.admin_service)

@admin_routes.route("/v1/admin/dashboard", methods=["GET"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    }
  ],
  "responses": {
    200: {
      "description": "Retrieve dashboard data sucessfully",
      "schema": {
        "type": "object",
        "properties": {
          "active_subscriptions": {"type": "integer", "example": 420},
          "total_models": {"type": "integer", "example": 20},
          "total_revenue": {"type": "number", "example": 49999.99},
          "total_users": {"type": "integer", "example": 300},
        }
      }
    }
  }
})
def get_dashboard(current_user_id):
  return admin_controller.get_dashboard()

@admin_routes.route("/v1/admin/revenue", methods=["GET"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    }
  ],
  "responses": {
    200: {
      "description": "Retrieve revenue data sucessfully",
      "schema": {
        "type": "object",
        "properties": {
          "revenue_by_month": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "month": {"type": "string", "example": "Sat, 01 Feb 2025 00:00:00 GMT"},
                "total_revenue": {"type": "number", "example": 8999999.5}
              }
            }
          }
        }
      }
    }
  }
})
def get_revenue(current_user_id):
  return admin_controller.get_revenue()

@admin_routes.route("/v1/admin/model-usage", methods=["GET"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    }
  ],
  "responses": {
    200: {
      "description": "Retrieve model usage data sucessfully",
      "schema": {
        "type": "object",
        "properties": {
          "model_usage": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": {"type": "string", "example": "prototype-1"},
                "value": {"type": "integer", "example": 20}
              },
            }
          }
        }
      }
    }
  }
})
def get_model_usage(current_user_id):
  return admin_controller.get_model_usage()

