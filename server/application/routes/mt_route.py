from flask import request, Blueprint, jsonify  # type: ignore
from flasgger import swag_from
from application.controllers.mt_controller import MtController
from application.container import container
from application.services.middleware import bot_token_required

mt_routes = Blueprint("mt_routes", __name__)
mt_controller = MtController(container.mt_service)

@mt_routes.route("/v1/mt/auth", methods=["GET"])
@swag_from({
  "tags": ["metatrader"],
  "summary": "Verify MetaTrader authentication token",
  "description": "This endpoint verifies the authenticity of the provided MetaTrader token.",
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
      "description": "Verify token successfully",
      "schema": {
        "type": "object",
        "properties": {
          "expert_id": {"type": "string"},
          "is_banned": {"type": "boolean"},
          "is_expert": {"type": "boolean"},
          "model_id": {"type": "string"},
          "portfolio_id": {"type": "string"}
        }
      }
    },
    401: {
      "description": "Unauthorized - Invalid or missing token",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Unauthorized"},
          "status": {"type": "integer", "example": 401}
        }
      }
    }
  }
})
def verify_token():
  return mt_controller.verify_token(request)

@mt_routes.route("/v1/mt/order", methods=["POST"])
@swag_from({
  "tags": ["metatrader"],
  "summary": "Create a new order in MetaTrader",
  "description": "This endpoint allows users to create a new order in MetaTrader. "
                 "It requires a valid authorization token.",
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    }
  ],
  "requestBody": {
    "description": "Order details",
    "required": True,
    "content": {
      "application/json": {
        "schema": {
          "type": "object",
          "properties": {
            "order_id": {"type": "string"},
            "portfolio_id": {"type": "string"},
            "model_id": {"type": "string"},
            "order_type": {"type": "string", "example": "buy"},
            "symbol": {"type": "string", "example": "EURUSD"},
            "profit": {"type": "number", "example": 150.50},
            "volume": {"type": "number", "example": 1.0},
            "entry_price": {"type": "number", "example": 1.2345},
            "exit_price": {"type": "number", "example": 1.2500}
          },
          "required": ["order_id", "portfolio_id", "model_id", "order_type", "symbol", "volume", "entry_price"]
        }
      }
    }
  },
  "responses": {
    200: {
      "description": "Order sent successfully",
      "schema": {
        "type": "object",
        "properties": {
          "order_id": {"type": "string"},
          "portfolio_id": {"type": "string"},
          "model_id": {"type": "string"},
          "order_type": {"type": "string"},
          "symbol": {"type": "string"},
          "profit": {"type": "number"},
          "volume": {"type": "number"},
          "entry_price": {"type": "number"},
          "exit_price": {"type": "number"}
        }
      }
    },
    400: {
      "description": "Bad request - Invalid input",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Invalid order data"},
          "status": {"type": "integer", "example": 400}
        }
      }
    }
  }
})
@bot_token_required
def create_order(user_id, portfolio_id):
  return mt_controller.create_order(request)
