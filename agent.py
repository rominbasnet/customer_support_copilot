"""
The agent: takes a ticket, gives GPT the ticket + tools, lets it call
tools as needed (in a loop), and returns a drafted reply plus a trace
of every tool call made (useful for debugging + evals later).
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOL_FUNCTIONS, TOOL_SCHEMAS as _RAW_SCHEMAS
from models import Ticket
load_dotenv()  # load .env file if present
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MODEL = "gpt-4o"

SYSTEM_PROMPT = """You are a customer support agent for an e-commerce company.

You will be given a customer's support ticket. Use the available tools to:
1. Look up the relevant order.
2. Check shipping status if the customer is asking about delivery.
3. Issue a refund ONLY if the order is refund-eligible and the customer's
   request justifies it. Never issue a refund without first calling
   lookup_order to confirm eligibility.

After gathering the information you need, write a short, friendly,
professional reply to the customer explaining what you found and what
action (if any) you took. Do not invent information you did not get
from a tool call.
"""

# OpenAI wants tool schemas in a different shape than Anthropic:
#   Anthropic: {"name": ..., "description": ..., "input_schema": {...}}
#   OpenAI:    {"type": "function", "function": {"name": ..., "description": ..., "parameters": {...}}}
# tools.py defines schemas in Anthropic's shape (input_schema), so we
# convert the key name here.
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": schema["name"],
            "description": schema["description"],
            "parameters": schema["input_schema"],
        },
    }
    for schema in _RAW_SCHEMAS
]


def process_ticket(ticket: Ticket) -> dict:
    """Runs the tool-calling loop for one ticket. Returns the draft
    reply and a trace of every tool call made along the way."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Customer ID: {ticket.customer_id}\n"
                f"Order ID: {ticket.order_id}\n"
                f"Message: {ticket.message}"
            ),
        },
    ]

    tool_trace = []
    max_turns = 6  # safety valve against infinite tool-call loops

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=OPENAI_TOOLS,
        )

        choice = response.choices[0]
        message = choice.message

        # If GPT wants to call tool(s), finish_reason == "tool_calls"
        if choice.finish_reason == "tool_calls":
            # Append the assistant's tool-call message before responding
            messages.append(message.model_dump(exclude_unset=True))

            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                fn = TOOL_FUNCTIONS.get(fn_name)
                result = fn(**fn_args) if fn else {"error": "unknown tool"}

                tool_trace.append({
                    "tool": fn_name,
                    "input": fn_args,
                    "result": result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })

            continue  # let GPT see the results and decide next step

        # No more tools needed — this is the final drafted reply
        return {"draft_reply": message.content, "tool_trace": tool_trace}

    return {
        "draft_reply": "Could not resolve this ticket automatically — "
                       "escalating to a human agent.",
        "tool_trace": tool_trace,
    }