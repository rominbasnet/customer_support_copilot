"""
The 'internal APIs' the agent is allowed to call.

Each tool has:
  1. A real Python function that does the work (against our fake DB).
  2. A JSON schema describing it to the LLM, so the model knows the
     tool exists and what arguments it takes.

In a real company, lookup_order() would call an internal orders
microservice instead of a dict.
"""
from models import orders_db


# ---------- 1. Real implementations ----------

def lookup_order(order_id: int) -> dict:
    order = orders_db.get(order_id)
    if not order:
        return {"error": f"No order found with id {order_id}"}
    return order.model_dump()


def issue_refund(order_id: int, reason: str) -> dict:
    order = orders_db.get(order_id)
    if not order:
        return {"error": f"No order found with id {order_id}"}
    if not order.refundable:
        return {
            "success": False,
            "message": f"Order {order_id} is not eligible for a refund "
                       f"(status: {order.status})."
        }
    # In real life: call payments API, update DB, etc.
    return {
        "success": True,
        "message": f"Refund of ${order.price} issued for order {order_id}.",
        "reason": reason,
    }


def check_shipping_status(order_id: int) -> dict:
    order = orders_db.get(order_id)
    if not order:
        return {"error": f"No order found with id {order_id}"}
    return {"order_id": order_id, "status": order.status}


# Dispatch table: tool name (string) -> Python function
TOOL_FUNCTIONS = {
    "lookup_order": lookup_order,
    "issue_refund": issue_refund,
    "check_shipping_status": check_shipping_status,
}


# ---------- 2. Schemas the LLM sees ----------

TOOL_SCHEMAS = [
    {
        "name": "lookup_order",
        "description": "Look up an order's details (item, price, status, "
                        "whether it's refund-eligible) by order id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "The order ID."}
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "issue_refund",
        "description": "Issue a refund for an order, if it is eligible. "
                        "Only call this after confirming the order is "
                        "refundable via lookup_order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "The order ID."},
                "reason": {"type": "string", "description": "Why the refund is being issued."},
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "name": "check_shipping_status",
        "description": "Check the current shipping/delivery status of an order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "The order ID."}
            },
            "required": ["order_id"],
        },
    },
]