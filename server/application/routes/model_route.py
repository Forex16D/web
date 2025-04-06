from flask import request, Blueprint  # type: ignore
from flasgger import swag_from  # Import Flasgger

from application.container import container
from application.controllers.model_controller import ModelController
from application.services.middleware import admin_required, token_required

model_routes = Blueprint("model_routes", __name__)
model_controller = ModelController(container.model_service)

# Public Endpoints
@model_routes.route("/v1/models/public", methods=["GET"])
@swag_from({
  'tags': ['model'],
  'summary': 'List of active models',
  'responses': {
    200: {
      'description': 'List of active models',
      'schema': {
        'type': 'array',
        'items': {
          'type': 'object',
          'properties': {
            'active': {
              'type': 'boolean',
              'example': True
            },
            'auto_train': {
              'type': 'boolean',
              'example': True
            },
            'commission': {
              'type': 'number',
              'format': 'float',
              'example': 0.15
            },
            'created_at': {
              'type': 'string',
              'format': 'date-time',
              'example': '2025-03-27T09:46:26Z'
            },
            'file_path': {
              'type': 'string',
              'example': 'models/ba8350f3-db7e-48b2-a615-fc55f8d75c24'
            },
            'model_id': {
              'type': 'string',
              'format': 'uuid',
              'example': 'ba8350f3-db7e-48b2-a615-fc55f8d75c24'
            },
            'monthly_pnl': {
              'type': 'number',
              'format': 'float',
              'example': 0.0
            },
            'name': {
              'type': 'string',
              'example': 'prototype-1'
            },
            'symbol': {
              'type': 'string',
              'example': 'EURUSD'
            },
            'updated_at': {
              'type': 'string',
              'format': 'date-time',
              'example': '2025-04-01T01:56:07Z'
            },
            'weekly_profits': {
              'type': 'array',
              'items': {
                'type': 'object',
                'properties': {
                  'model_id': {
                    'type': 'string',
                    'format': 'uuid',
                    'example': 'ba8350f3-db7e-48b2-a615-fc55f8d75c24'
                  },
                  'week_start': {
                    'type': 'string',
                    'format': 'date-time',
                    'example': '2025-02-10T00:00:00Z'
                  },
                  'weekly_profit': {
                    'type': 'number',
                    'format': 'float',
                    'example': 0.0
                  }
                }
              }
            }
          }
        }
      }
    }
  }
})
def get_user_models():
  return model_controller.get_active_models()

@model_routes.route("/v1/models/<model_id>", methods=["GET"])
@swag_from({
  'tags': ['model'],
  'summary': 'Get a specific model by ID',
  'parameters': [
    {
      'name': 'model_id',
      'in': 'path',
      'type': 'string',
      'required': True,
      'description': 'The UUID of the model to retrieve',
      'example': 'bf72a573-b4fc-446b-bb16-9d0a373b2954'
    }
  ],
  'responses': {
    200: {
      'description': 'Details of the model',
      'schema': {
        'type': 'object',
        'properties': {
          'active': {
            'type': 'boolean',
            'example': True
          },
          'auto_train': {
            'type': 'boolean',
            'example': False
          },
          'commission': {
            'type': 'number',
            'format': 'float',
            'example': 0.335
          },
          'created_at': {
            'type': 'string',
            'format': 'date-time',
            'example': '2025-02-28T11:32:55Z'
          },
          'file_path': {
            'type': 'string',
            'example': 'models/bf72a573-b4fc-446b-bb16-9d0a373b2954'
          },
          'model_id': {
            'type': 'string',
            'format': 'uuid',
            'example': 'bf72a573-b4fc-446b-bb16-9d0a373b2954'
          },
          'name': {
            'type': 'string',
            'example': 'MOAM'
          },
          'symbol': {
            'type': 'string',
            'example': 'USDJPY'
          },
          'updated_at': {
            'type': 'string',
            'format': 'date-time',
            'example': '2025-04-05T03:17:41Z'
          }
        }
      }
    },
    404: {
      'description': 'Model not found'
    }
  }
})
def get_model_detail(model_id):
  return model_controller.get_model_detail(model_id)

# User-Protected Endpoints
@model_routes.route("/v1/models/<model_id>/copy", methods=["PUT"])
@token_required
@swag_from({
  "tags": ["model"],
  "parameters": [
    {
      "name": "model_id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "ID of the model to copy"
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
def copy_trade(current_user_id, model_id):
  return model_controller.copy_trade(request, model_id, current_user_id)

# Admin-Protected Endpoints
@model_routes.route("/v1/models", methods=["GET"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "summary": "List of all models",
  'responses': {
    200: {
      'description': 'List of all models',
      'schema': {
        'type': 'array',
        'items': {
          'type': 'object',
          'properties': {
            'active': {
              'type': 'boolean',
              'example': True
            },
            'auto_train': {
              'type': 'boolean',
              'example': True
            },
            'commission': {
              'type': 'number',
              'format': 'float',
              'example': 0.15
            },
            'created_at': {
              'type': 'string',
              'format': 'date-time',
              'example': '2025-03-27T09:46:26Z'
            },
            'file_path': {
              'type': 'string',
              'example': 'models/ba8350f3-db7e-48b2-a615-fc55f8d75c24'
            },
            'model_id': {
              'type': 'string',
              'format': 'uuid',
              'example': 'ba8350f3-db7e-48b2-a615-fc55f8d75c24'
            },
            'monthly_pnl': {
              'type': 'number',
              'format': 'float',
              'example': 0.0
            },
            'name': {
              'type': 'string',
              'example': 'prototype-1'
            },
            'symbol': {
              'type': 'string',
              'example': 'EURUSD'
            },
            'updated_at': {
              'type': 'string',
              'format': 'date-time',
              'example': '2025-04-01T01:56:07Z'
            },
          }
        }
      }
    }
  }
})
def get_models(current_user_id):
  return model_controller.get_all_models(request)

@model_routes.route("/v1/models", methods=["POST"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "summary": "Create a new model",
  "parameters": [
    {
      "name": "files[]",
      "in": "formData",
      "type": "file",
      "required": True,
      "description": "Model file to upload"
    },
  ],
  "responses": {
    201: {
      "description": "Model created successfully",
      "schema": {
        "type": "object",
        "properties": {
          "message": {
            "type": "string",
            "description": "Success message",
            "example": "Model created successfully!"
          },
        }
      }
    }
  }
})
def create_models(current_user_id):
  return model_controller.create_models(request, current_user_id)

@model_routes.route("/v1/models/<model_id>", methods=["DELETE"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "parameters": [
    {
      "name": "model_id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "ID of the model to delete"
    }
  ],
  "responses": {
    200: {
      "description": "Model deleted successfully",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "description": "Success message", "example": "Model deleted successfully!"}
        }
      }
    }
  }
})
def delete_model(current_user_id, model_id):
  return model_controller.delete_model(model_id, current_user_id)

@model_routes.route("/v1/models/<model_id>/train", methods=["POST"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "summary": "Train a model",
  "parameters": [
    {
      "name": "model_id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "ID of the model to train"
    }
  ],
  "responses": {
    200: {
      "description": "Model training started",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "description": "Success message", "example": "Model trained successfully!"}
        }
      }
    }
  }
})
def train_model(current_user_id, model_id):
  return model_controller.train_model(model_id, request)

@model_routes.route("/v1/models/<model_id>/backtest", methods=["POST"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "parameters": [
    {
      "name": "model_id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "ID of the model to backtest"
    }
  ],
  "responses": {
    200: {
      "description": "Model backtesting started",
      "schema": {"type": "object"}
    }
  }
})
def backtest_model(current_user_id, model_id):
  return model_controller.backtest_model(model_id)

@model_routes.route("/v1/models/<model_id>/evaluate/stop", methods=["POST"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "parameters": [
    {
      "name": "model_id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "ID of the model to stop evaluation"
    }
  ],
  "responses": {
    200: {
      "description": "Model evaluation stopped",
      "schema": {"type": "object"}
    }
  }
})
def stop_evaluate(current_user_id, model_id):
  return model_controller.stop_evaluate(model_id)

@model_routes.route("/v1/models/status", methods=["GET"])
@admin_required
def get_processes_status(current_user_id):
  return model_controller.get_processes_status()

@model_routes.route("/v1/models/<model_id>/status", methods=["GET"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "responses": {
    200: {
      "description": "Status of all processes",
      "schema": {
        "type": "object",
        "properties": {
          "model_id": {"type": "string", "example": "ba8350f3-db7e-48b2-a615-fc55f8d75c24"},
          "running": {"type": "boolean", "example": True},
        }
      }
    }
  }
})
def get_process_status(current_user_id, model_id):
  return model_controller.get_process_status(model_id)

@model_routes.route("/v1/models/<model_id>", methods=["PUT"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "parameters": [
    {
      "name": "model_id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "ID of the model to update"
    }
  ],
  "responses": {
    200: {
      "description": "Model updated successfully",
      "schema": {"type": "object"}
    }
  }
})
def update_model(current_user_id, model_id):
  return model_controller.update_model(request, model_id)

@model_routes.route("/v1/models/backtest/stream", methods=["GET"])
@admin_required
@swag_from({
  "tags": ["admin"],
  "responses": {
    200: {
      "description": "Stream backtest status",
      "schema": {"type": "object"}
    }
  }
})
def stream_status(current_user_id):
  return model_controller.stream_backtest_status()