from flask import request, Blueprint # type: ignore
from flasgger import swag_from

from application.controllers.auth_controller import AuthController
from application.container import container

auth_routes = Blueprint("auth_routes", __name__)
auth_controller = AuthController(container.auth_service)

@auth_routes.route("/v1/login", methods=["POST"])
@swag_from({
  "tags": ["auth"],
  "parameters": [
    {
     "in": "body",
      "required": True,
      "schema": {
        "type": "object",
        "properties": {
          "email": {
            "type": "string",
            "description": "The email of the user"
          },
          "password": {
            "type": "string",
            "description": "The password of the user"
          },
          "remember": {
            "type": "boolean",
            "description": "Remember user"
          },
        }
      }
    }
  ],
  "responses": {
    200: {
      "description": "Login to website",
      "schema": {
        "type": "object",
        "properties": {
          "token": {
            "type": "string",
            "description": "Authentication token to use for future requests"
          },
        }
      }
    }
  },
  "consumes": ["application/json"],
  "produces": ["application/json"],
})
def login():
  return auth_controller.login(request)

@auth_routes.route("/v1/register", methods=["POST"])
@swag_from({
  "tags": ["auth"],
  "parameters": [
    {
     "in": "body",
      "required": True,
      "schema": {
        "type": "object",
        "properties": {
          "email": {
            "type": "string",
            "description": "The email of the user"
          },
          "password": {
            "type": "string",
            "description": "The password of the user"
          },
          "confirmPassword": {
            "type": "string",
            "description": "Confirm password of the user"
          },
        }
      }
    }
  ],
  "responses": {
    200: {
      "description": "Login to website",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "description": "Response message from the server", "example": "User registered successfully!"}
        }
      }
    }
  },
  "consumes": ["application/json"],
  "produces": ["application/json"],
})
def register():
  return auth_controller.register(request)

@auth_routes.route("/v1/auth", methods=["GET"])
@swag_from({
  "tags": ["auth"],
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
      "description": "Verify the user and authentication status",
      "schema": {
        "type": "object",
        "properties": {
          "authentication": {
            "type": "boolean",
            "description": "Indicates whether the user is authenticated"
          },
          "is_admin": {
            "type": "boolean",
            "description": "Indicates whether the user has admin privileges"
          },
        }
      }
    },
    401: {
      "description": "Unauthorized - Invalid or missing token",
      "schema": {
        "type": "object",
        "properties": {
          "message": {
            "type": "string",
            "description": "Response message from the server",
            "example": "Unauthorized"
          },
          "status": {
            "type": "integer",
            "description": "HTTP response status code",
            "example": 401
          }
        }
      }
    }
  },
  "consumes": ["application/json"],
  "produces": ["application/json"],
})
def verify_user():
    return auth_controller.verify_user(request)
