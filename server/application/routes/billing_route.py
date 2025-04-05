from flask import request, Blueprint # type: ignore
from flasgger import swag_from # type: ignore

from application.controllers.billing_controller import BillingController
from application.container import container
from application.services.middleware import  token_required, admin_required
bill_routes = Blueprint("bill_routes", __name__)
bill_controller = BillingController(container.billing_service)

@bill_routes.route("/v1/bills", methods=["GET"])
@swag_from({
  "tags": ["billing"],
  "summary": "Retrieve all bills",
  "description": "This endpoint retrieves all bills for the authenticated user.",
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
      "description": "Retrieve all bills successfully",
      "schema": {
        "type": "object",
        "properties": {
          "bills": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "bill_id": {"type": "integer", "example": 1},
                "created_at": {"type": "string", "example": "Tue, 25 Mar 2025 03:06:58 GMT"},
                "due_date": {"type": "string", "example": "Tue, 25 Mar 2025 00:00:00 GMT"},
                "exchange_rate": {"type": "number", "example": 34.00},
                "net_amount": {"type": "number", "example": 816},
                "net_amount_usd": {"type": "number", "example": 24.00},
                "status": {"type": "string", "example": "paid"},
                "user_id": {"type": "string", "example": "a4-b3-4c2e-8f5d-1a2b3c4d5e6f"},
              }
            },
          }
        }
     },
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
@token_required
def get_bills(current_user_id):
  return bill_controller.get_bills(current_user_id)

@bill_routes.route("/v1/bills/<bill_id>", methods=["GET"])
@swag_from({
  "tags": ["billing"],
  "summary": "Retrieve a specific bill",
  "description": "This endpoint retrieves a specific bill by its ID.",
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
    {
      "name": "bill_id",
      "in": "path",
      "type": "integer",
      "required": True,
      "description": "ID of the bill to retrieve"
    }
  ],
  "responses": {
    200: {
      "description": "Retrieve bill successfully",
      "schema": {
        "type": "object",
        "properties": {
          "bill": {
            "type": "object",
            "properties": {
              "bill_id": {"type": "integer", "example": 1},
              "created_at": {"type": "string", "example": "Tue, 25 Mar 2025 03:06:58 GMT"},
              "due_date": {"type": "string", "example": "Tue, 25 Mar 2025 00:00:00 GMT"},
              "exchange_rate": {"type": "number", "example": 34.00},
              "net_amount": {"type": "number", "example": 816},
              "net_amount_usd": {"type": "number", "example": 24.00},
              "status": {"type": "string", "example": "paid"},
              "user_id": {"type": "string", "example": "a4-b3-4c2e-8f5d-1a2b3c4d5e6f"},
            }
          }
        }
      },
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
@token_required
def get_bill(current_user_id, bill_id):
  return bill_controller.get_bill(current_user_id, bill_id)

@bill_routes.route("/v1/bills/<bill_id>/orders", methods=["GET"])
@swag_from({
  "tags": ["billing"],
  "summary": "Retrieve all orders for a specific bill",
  "description": "This endpoint retrieves all orders for a specific bill by its ID.",
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
    {
      "name": "bill_id",
      "in": "path",
      "type": "integer",
      "required": True,
      "description": "ID of the bill to retrieve orders for"
    }
  ],
  "responses": {
    200: {
      "description": "Retrieve orders successfully",
      "schema": {
        "type": "object",
        "properties": {
          "orders": {
            "type": "array",
            "properties": {
              "bill_id": { "type": "integer", "example": 8 },
              "commission": { "type": "number", "example": 0.335 },
              "created_at": { "type": "string", "example": "Thu, 06 Mar 2025 06:00:01 GMT" },
              "entry_price": { "type": "number", "example": 105 },
              "exit_price": { "type": "number", "example": 210 },
              "model_id": { "type": "string", "example": "bf72a573-b4fc-446b-bb16-9d0a373b2954" },
              "order_id": { "type": "integer", "example": 123457 },
              "order_type": { "type": "string", "example": "buy" },
              "portfolio_id": { "type": "string", "example": "0752d071-7767-45b1-8d9d-f24c88d247c9" },
              "profit": { "type": "number", "example": 120 },
              "symbol": { "type": "string", "example": "EURUSD" },
              "volume": { "type": "number", "example": 0.1 }
            }
          }
        }
     },
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
  
@token_required
def get_orders(current_user_id, bill_id):
  return bill_controller.get_orders(bill_id)

@bill_routes.route("/v1/payments", methods=["POST"])
@swag_from({
  "tags": ["billing"],
  "summary": "Pay a bill",
  "description": "This endpoint pays a bill using either a receipt or wallet.",
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
    {
      "name": "bill_id",
      "in": "body",
      "type": "integer",
      "required": True,
      "description": "ID of the bill to be paid"
    },
    {
      "name": "note",
      "in": "body",
      "type": "integer",
      "required": False,
      "description": "Notes for the payment"
    },
    {
      "name": "method",
      "in": "body",
      "type": "string",
      "required": True,
      "description": "Method of payment (receipt or wallet)"
    },
    {
      "name": "receipt_image",
      "in": "body",
      "type": "file",
      "required": True,
      "description": "Image of the receipt (if method is receipt)"
    },
  ],
  "responses": {
    200: {
      "description": "Payment processed successfully",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Payment Successful!"},
          "status": {"type": "integer", "example": 200},
        }
      }
    },
    400: {
      "description": "Bad Request - Invalid input",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Bad Request"},
          "status": {"type": "integer", "example": 400},
        }
      }
    },
    401: {
      "description": "Unauthorized - Invalid or missing token",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Unauthorized"},
          "status": {"type": "integer", "example": 401},
        }
      }
    }
  }
})  
@token_required
def pay_bill(current_user_id):
  return bill_controller.pay_bill(current_user_id, request)

@bill_routes.route("/v1/withdrawals", methods=["POST"])
@swag_from({
  "tags": ["billing"],
  "summary": "Create a withdrawal request",
  "description": "This endpoint allows users to create a withdrawal request.",
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
    {
      "name": "amount",
      "in": "body",
      "type": "number",
      "required": True,
      "description": "Amount to withdraw"
    },
    {
      "name": "method",
      "in": "body",
      "type": "string",
      "required": True,
      "description": "Method of withdrawal (bank or crypto)"
    },
    {
      "name": "bank_account",
      "in": "body",
      "type": "string",
      "required": True,
      "description": "Bank account details (if method is bank)"
    },
    {
      "name": "wallet_address",
      "in": "body",
      "type": "file",
      "required": True,
      "description": "Wallet address (if method is crypto)"
    },
  ],
  "responses": {
    200: {
      "description": "Withdrawal request created successfully",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "success"},
          "status": {"type": "integer", "example": 200},
        }
      }
    },
    400: {
      "description": "Bad Request - Invalid input",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Bad Request"},
          "status": {"type": "integer", "example": 400},
        }
      }
    },
    401: {
      "description": "Unauthorized - Invalid or missing token",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Unauthorized"},
          "status": {"type": "integer", "example": 401},
        }
      }
    }
  }
})  
@token_required
def create_withdraw_request(current_user_id):
  return bill_controller.create_withdraw_request(current_user_id, request)

@bill_routes.route("/v1/withdrawals/<withdraw_id>/<action>", methods=["PUT"])
@swag_from({
  "tags": ["admin"],
  "summary": "Update withdrawal request status",
  "description": "This endpoint allows admin to update the status of a withdrawal request.",
  "parameters": [
    {
      "name": "Authorization",
      "in": "header",
      "type": "string",
      "required": True,
      "description": "Bearer <your_token_here>"
    },
    {
      "name": "withdraw_id",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "ID of the withdrawal request to update"
    },
    {
      "name": "action",
      "in": "path",
      "type": "string",
      "required": True,
      "description": "Status action to perform (approved or rejected)"
    },
  ],
  "responses": {
    200: {
      "description": "Withdrawal request updated successfully",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "success"},
          "status": {"type": "integer", "example": 200},
        }
      }
    },
    400: {
      "description": "Bad Request - Invalid input",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Bad Request"},
          "status": {"type": "integer", "example": 400},
        }
      }
    },
    401: {
      "description": "Unauthorized - Invalid or missing token",
      "schema": {
        "type": "object",
        "properties": {
          "message": {"type": "string", "example": "Unauthorized"},
          "status": {"type": "integer", "example": 401},
        }
      }
    }
  }
})  
@admin_required
def update_withdraw_request_status(current_user_id, withdraw_id, action):
  return bill_controller.update_withdraw_request_status(current_user_id, withdraw_id, action)

@bill_routes.route("/v1/withdrawals/admin", methods=["GET"])
@swag_from({
  "tags": ["admin"],
  "summary": "Retrieve all withdrawal requests",
  "description": "This endpoint retrieves all withdrawal requests for admin.",
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
      "description": "Retrieve withdrawal requests successfully",
      "schema": {
        "type": "object",
        "properties": {
          "withdrawals": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "requests": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "amount": {
                        "type": "string",
                        "description": "The amount requested for withdrawal",
                        "example": "33.00"
                      },
                      "approved_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Date and time when the request was approved",
                        "example": "Sat, 29 Mar 2025 15:22:35 GMT"
                      },
                      "bank_account": {
                        "type": "string",
                        "description": "The bank account number associated with the withdrawal",
                        "example": "1111111111"
                      },
                      "created_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Date and time when the withdrawal request was created",
                        "example": "Sat, 29 Mar 2025 08:31:48 GMT"
                      },
                      "method": {
                        "type": "string",
                        "description": "The withdrawal method used",
                        "example": "bank"
                      },
                      "status": {
                        "type": "string",
                        "description": "Current status of the withdrawal request",
                        "example": "approved"
                      },
                      "user_id": {
                        "type": "string",
                        "description": "Unique identifier of the user who made the request",
                        "example": "22ab89a8-393c-42a2-8e90-c6754f982d38"
                      },
                      "wallet_address": {
                        "type": ["string", "null"],
                        "description": "Wallet address for crypto withdrawals (null if not applicable)",
                        "example": None
                      },
                      "withdraw_id": {
                        "type": "integer",
                        "description": "Unique identifier for the withdrawal request",
                        "example": 2
                      }
                    }
                  }
                }
              }
            }
          }
        }
     },
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
def get_withdraw_requests_admin():
  return bill_controller.get_withdraw_requests_admin()