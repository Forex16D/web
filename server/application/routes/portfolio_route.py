from flask import request, Blueprint, jsonify # type: ignore
from flasgger import swag_from # type: ignore

from application.services.middleware import token_required
from application.controllers.portfolio_controller import PortfolioController
from application.container import container

portfolio_routes = Blueprint("portfolio_routes", __name__)

portfolio_controller = PortfolioController(container.portfolio_service)

@portfolio_routes.route("/v1/portfolios", methods=["GET"])
@swag_from({
  "tags": ["portfolio"],
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
      "description": "Get all portfolios",
      "schema": {
        "type": "array",
        "items": {
          "properties": {
            "commission": {
              "type": "string",
              "description": "Commission percentage",
              "example": "0.75"
            },
            "connected": {
              "type": "boolean",
              "description": "Indicates whether the user is connected",
              "example": False
            },
            "created_at": {
              "type": "string",
              "format": "date-time",
              "description": "Timestamp when the record was created",
              "example": "Mon, 03 Mar 2025 13:18:37 GMT"
            },
            "expert_id": {
              "type": ["string", "null"],
              "description": "Unique identifier for the expert (null if not an expert)",
              "example": None
            },
            "is_expert": {
              "type": "boolean",
              "description": "Indicates whether the user is an expert",
              "example": True
            },
            "login": {
              "type": "integer",
              "description": "User login ID",
              "example": 2546821
            },
            "lot_size": {
              "type": "string",
              "description": "Size of the trading lot",
              "example": "0"
            },
            "model_id": {
              "type": "string",
              "description": "Unique identifier of the trading model",
              "example": "ba8350f3-db7e-48b2-a615-fc55f8d75c24"
            },
            "model_name": {
              "type": "string",
              "description": "Name of the trading model",
              "example": "prototype-1"
            },
            "monthly_pnl": {
              "type": "number",
              "description": "Monthly profit and loss",
              "example": 0
            },
            "name": {
              "type": "string",
              "description": "User or account name",
              "example": "Tradingm@ster"
            },
            "portfolio_id": {
              "type": "string",
              "description": "Unique identifier of the portfolio",
              "example": "0752d071-7767-45b1-8d9d-f24c88d247c9"
            },
            "total_profit": {
              "type": "number",
              "description": "Total profit earned",
              "example": 1245.53
            },
            "user_id": {
              "type": "string",
              "description": "Unique identifier of the user",
              "example": "22ab89a8-393c-42a2-8e90-c6754f982d38"
            },
            "winrate": {
              "type": "string",
              "description": "User's win rate percentage",
              "example": "100.0000000000000000"
            }
          }
        }
      }
    }
  },
  "produces": ["application/json"],
  "consumes": ["application/json"],
})
@token_required
def get_portfolios(current_user_id):
  return portfolio_controller.get_portfolios(current_user_id)

@portfolio_routes.route("/v1/portfolios", methods=["POST"])
@token_required
@swag_from({
  "tags": ["portfolio"],
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
    {
      "name": "name",
      "in": "body",
      "required": True,
      "description": "Name of the portfolio",
    },
    {
      "name": "login",
      "in": "body",
      "required": True,
      "description": "metatrader Login",
    }
  ],
})
def create_portfolio(current_user_id):
  return portfolio_controller.create_portfolio(request, current_user_id)

@portfolio_routes.route("/v1/portfolios/<portfolio_id>", methods=["GET", "PUT", "DELETE"])
@token_required
def portfolio_by_id(current_user_id, portfolio_id):
  if request.method == "GET":
    return portfolio_controller.get_portfolio(portfolio_id, current_user_id)
  elif request.method == "PUT":
    return portfolio_controller.update_portfolio(request, portfolio_id)
  elif request.method == "DELETE":
    return portfolio_controller.delete_portfolio(portfolio_id, current_user_id)
  return jsonify({"error": "Method not allowed"}), 405

@portfolio_routes.route("/v1/expert-portfolios", methods=["GET"])
@swag_from({
  'tags': ['portfolio'],
  'summary': 'Get list of expert portfolios with performance metrics',
  'responses': {
    200: {
      'description': 'List of expert portfolios with stats',
      'schema': {
        'type': 'array',
        'items': {
          'type': 'object',
          'properties': {
            'connected': {
              'type': 'boolean',
              'example': True
            },
            'created_at': {
              'type': 'string',
              'format': 'date-time',
              'example': '2025-02-15T10:00:00Z'
            },
            'is_expert': {
              'type': 'boolean',
              'example': True
            },
            'name': {
              'type': 'string',
              'example': 'AlphaTrader'
            },
            'portfolio_id': {
              'type': 'string',
              'format': 'uuid',
              'example': 'd6cfc7ee-2b18-4634-b81c-f89e0c31c923'
            },
            'user_id': {
              'type': 'string',
              'format': 'uuid',
              'example': '5f4d5b97-3320-4fc1-a14f-f7a86f768e1e'
            },
            'commission': {
              'type': 'number',
              'format': 'float',
              'example': 0.25
            },
            'total_profit': {
              'type': 'number',
              'format': 'float',
              'example': 12035.50
            },
            'monthly_pnl': {
              'type': 'number',
              'format': 'float',
              'example': 2200.75
            },
            'winrate': {
              'type': 'number',
              'format': 'float',
              'example': 67.5,
              'description': 'Percentage of profitable orders'
            }
          }
        }
      }
    }
  }
})
def get_expert_portfolios():
  return portfolio_controller.get_expert_portfolios()

@portfolio_routes.route("/v1/portfolios/<portfolio_id>/commission", methods=["GET"])
def get_portfolio_commission(portfolio_id):
  return portfolio_controller.get_portfolio_commission(portfolio_id)

@portfolio_routes.route("/v1/portfolios/commission", methods=["GET"])
@token_required
@swag_from({
  "tags": ["portfolio"],
  "summary": "Get total commission for the user",
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
      "description": "Total commission for the user",
      "schema": {
        "type": "array",
        "items": {
          "properties": {
            "name": {
              "type": "string",
              "example": "portfolio name"
            },
            "total_profit": {
              "type": "number",
              "example": 150.75
            }
          },  
        }
      }
    }
  }
})
def get_total_commission(current_user_id):
  return portfolio_controller.get_total_commission(current_user_id)

@portfolio_routes.route("/v1/balance", methods=["GET"])
@token_required
@swag_from({
  "tags": ["portfolio"],
  "summary": "Get total commission for the user",
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
      "description": "Total commission for the user",
      "schema": {
        "type": "object",
        "properties": {
          "balance": {
            "type": "number",
            "example": 500
          }
        },  
      }
    }
  }
})
def get_user_balance(current_user_id):
  return portfolio_controller.get_user_balance(current_user_id)

@portfolio_routes.route("/v1/portfolios/<expert_id>/copy", methods=["PUT"])
@token_required
@swag_from({
  "tags": ["model"],
  "parameters": [
    {
    "name": "Authorization",
    "in": "header",
    "type": "string",
    "required": True,
    "description": "Bearer <your_token_here>"
    },
    {
      "name": "expert_id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "ID of the expert's portfolio to copy"
    },
    {
      "name": "portfolio_id",
      "in": "body",
      "type": "string",
      "required": True,
      "description": "ID of user portfolio to copy the model to",
    },
  ],
  "responses": {
    200: {
      "description": "Copy trade success",
      "schema": {
        "type": "object",
        "properties": {
          "message": {
            "type": "string",
            "description": "Success message",
            "example": "Copy trade successfully!"
          }
        }
      }
    }
  }
})
def copy_trade(current_user_id, expert_id):
  return portfolio_controller.copy_trade(request, expert_id, current_user_id)
