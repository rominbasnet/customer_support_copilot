from fastapi import FastAPI, HTTPException
from models import (
    Order, Ticket, TicketCreate, TicketStatus,
    orders_db, tickets_db, seed_orders, create_ticket,
)
from agent import process_ticket

app = FastAPI(title="Customer Support Copilot")


@app.on_event("startup")
def startup():
    seed_orders()


# ---------- Orders (read-only for this demo) ----------

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@app.get("/orders")
def list_orders():
    return list(orders_db.values())


# ---------- Tickets ----------

@app.post("/tickets", response_model=Ticket)
def new_ticket(data: TicketCreate):
    if data.order_id not in orders_db:
        raise HTTPException(400, "order_id does not exist")
    return create_ticket(data)


@app.get("/tickets", response_model=list[Ticket])
def list_tickets():
    return list(tickets_db.values())


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: int):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return ticket


@app.post("/tickets/{ticket_id}/process", response_model=Ticket)
def process(ticket_id: int):
    """Runs the AI agent on a ticket: looks up the order, decides
    whether to issue a refund, and drafts a reply."""
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    ticket.status = TicketStatus.processing
    result = process_ticket(ticket)

    ticket.draft_reply = result["draft_reply"]
    ticket.tool_trace = result["tool_trace"]
    ticket.status = TicketStatus.resolved

    return ticket