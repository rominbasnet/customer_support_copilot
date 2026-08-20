"""
In-memory 'database' for orders and tickets.

In a real system these would be SQLAlchemy models backed by Postgres.
Keeping it in-memory here so the project runs with zero setup.
"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class TicketStatus(str, Enum):
    open = "open"
    processing = "processing"
    resolved = "resolved"


# ---------- Schemas ----------

class Order(BaseModel):
    order_id: int
    customer_id: int
    item: str
    price: float
    status: str  # "delivered", "shipped", "processing"
    refundable: bool


class TicketCreate(BaseModel):
    customer_id: int
    order_id: int
    message: str


class Ticket(BaseModel):
    id: int
    customer_id: int
    order_id: int
    message: str
    status: TicketStatus = TicketStatus.open
    draft_reply: Optional[str] = None
    tool_trace: Optional[list] = None


# ---------- In-memory stores ----------

orders_db: dict[int, Order] = {}
tickets_db: dict[int, Ticket] = {}
_next_ticket_id = 1


def seed_orders():
    sample_orders = [
        Order(order_id=4521, customer_id=1, item="Wireless Headphones",
              price=59.99, status="delivered", refundable=True),
        Order(order_id=4522, customer_id=2, item="Phone Case",
              price=14.99, status="shipped", refundable=False),
        Order(order_id=4523, customer_id=3, item="Bluetooth Speaker",
              price=39.99, status="delivered", refundable=True),
    ]
    for o in sample_orders:
        orders_db[o.order_id] = o


def create_ticket(data: TicketCreate) -> Ticket:
    global _next_ticket_id
    ticket = Ticket(
        id=_next_ticket_id,
        customer_id=data.customer_id,
        order_id=data.order_id,
        message=data.message,
    )
    tickets_db[ticket.id] = ticket
    _next_ticket_id += 1
    return ticket