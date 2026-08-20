# Customer Support Copilot Agent

An AI-powered customer support copilot that reads support tickets, retrieves relevant information from internal systems, and drafts a response for the support agent.

The system uses **LLM function calling/tool use** to decide when it needs information from internal APIs, such as order details or refund information, before generating a response.


## Overview

Customer support agents often need to switch between a ticketing system and multiple internal tools to answer a customer's question.

For example, a customer might ask:

> "My order hasn't arrived yet. Can you check the status and tell me what I can do?"

Instead of manually searching for the order and checking different systems, the copilot can:

1. Read and understand the support ticket.
2. Determine what information is required.
3. Call the appropriate internal tool/API.
4. Use the returned information as context.
5. Draft a customer-facing response.
6. Leave the final decision and response approval to the human support agent.

---


## Key Features

###  Ticket Understanding

The agent processes incoming customer support tickets and identifies the customer's intent and the information needed to answer the request.

### 🔧 Tool / Function Calling

Instead of relying only on the model's existing knowledge, the agent can invoke internal tools when it needs real-time information.

Example tools include:

* `get_order(order_id)`
* `get_refund(order_id)`
* `process_refund(...)`

The model decides which tool is relevant based on the ticket and available context.

###  Order Lookup

The agent can retrieve order information such as order status and other relevant details from an internal order API.

### Refund Workflow

For refund-related requests, the agent can interact with the refund functionality rather than simply generating an answer based on assumptions.

###  Response Drafting

After gathering the required information, the agent generates a concise customer-facing response that can be reviewed and edited by a human support representative.

###  Human-in-the-Loop

The system is designed as a **copilot**, not an autonomous customer service bot.

The agent assists the support representative while keeping the human in control of the final response and potentially sensitive actions.

---

## Example Flow

### Input

```text
Customer:
"My order #12345 arrived damaged. Can I get a refund?"
```

### Agent reasoning flow

```text
Ticket
  ↓
Identify refund request
  ↓
Extract order ID
  ↓
Call order lookup tool
  ↓
Retrieve order information
  ↓
Determine refund-related information
  ↓
Call refund tool when appropriate
  ↓
Generate response
```

### Example Draft

```text
Hi,

I'm sorry that your order arrived damaged.

I've checked order #12345 and processed the refund according to our
refund policy. You should receive confirmation once the refund has
been processed.

Please let us know if you need anything else.

Best,
Support Team
```

The draft can then be reviewed by the support agent before being sent.

---

## Why Tool Calling?

A conventional LLM-only chatbot may attempt to answer questions using information contained in its context or training data.

That is not sufficient for customer support workflows because information such as:

* order status
* refund status
* customer information
* account state

can change frequently.

Tool calling allows the model to retrieve information from the systems that actually contain the current data.

The LLM is therefore responsible for **deciding what information it needs and how to use it**, while the tools remain responsible for accessing the underlying systems.

---

## Design Considerations

### Grounding Responses in Tool Results

The agent should use information returned by internal tools rather than inventing order or refund information.

### Separation of Reasoning and Actions

The model determines which tool may be required, while the application controls the actual tool execution.

This provides a boundary between the language model and internal business operations.

### Human Approval

Potentially sensitive operations can require human confirmation rather than allowing the model to execute them without review.

### Error Handling

The system should handle situations such as:

* Invalid order IDs
* Orders that cannot be found
* Failed API requests
* Refunds that are not eligible
* Missing information in the ticket
* Tool execution failures

---

## Tech Stack



```text
LLM:
OPENAI

Backend:
FastAPI, Python

Language:
Python

APIs:
FastAPI


```

---

## Project Structure

Example structure:

```text
.
├── agent/
│   ├── ...
│
├── tools/
│   ├── order_lookup.py
│   ├── refund.py
│   └── ...
│
├── api/
│   └── ...
│
├── tests/
│   └── ...
│
├── README.md
├── requirements.txt
└── ...
```

Update this section to match the actual repository structure.

---

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <project-directory>
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on the provided example:

```env
LLM_API_KEY=your_api_key
```

Do **not** commit API keys, credentials, or other secrets to the repository.

### 5. Run the application

