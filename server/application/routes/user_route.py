from flask import request, Blueprint # type: ignore
from flasgger import swag_from
from application.services.middleware import token_required, admin_required
from application.services.user import *
from application.container import container

from application.controllers.user_controller import UserController

user_routes = Blueprint("user_routes", __name__)
user_controller = UserController(container.user_service)

@user_routes.route("/v1/users", methods=["GET"])
@swag_from({
  "tags": ["admin"],
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
  ],
  "responses": {
    200: {
      "description": "Retrieve user profile successfully",
      "schema": {
        "type": "object",
        "properties": {
          "total_user": {"type": "integer", "example":100},
          "users": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "balance":{"type": "number", "example": 0.0},
                "created_at": {"type": "string", "example": "Mon, 31 Mar 2025 05:39:32 GMT"},
                "email": {"type": "string", "example":  "user@email.com"},
                "is_banned": {"type": "boolean", "example": False},
                "password": {"type": "string"},
                "role": {"type": "string", "example": "user"},
                "user_id": {"type": "string", "example": "f8492c63-af91-478b-bc63-e3847d625b02"}
              }
            }
          }
        }
      }
    }
  }
})
@admin_required
def get_users(current_user_id):
  return user_controller.get_all_users(request)

@user_routes.route("/v1/users/profile", methods=["GET"])
@swag_from({
  "tags": ["user"],
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
  ],
  "responses": {
    200: {
      "description": "Retrieve user profile successfully",
      "schema": {
        "type": "object",
        "properties": {
          "email": {"type": "string", "example": "user@email.com"}
        }
      }
    }
  }
})
@token_required
def get_user_profile(current_user_id):
  return user_controller.get_user_profile(current_user_id)

@user_routes.route("/v1/users/<user_id>", methods=["DELETE"])
@swag_from({
  "tags": ["user"],
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
    {
      "name": "user id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "Id of user to be delete"
    }
  ],
  "responses": {
    200: {
      "description": "User deleted successfully",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "User Deleted Successfully!"}
        }
      }
    }
  }
})
@admin_required
def delete_user(current_user_id, user_id):
  return user_controller.delete_user(current_user_id, user_id)

