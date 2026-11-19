# stallo-api

Backend for **Stallo**: sellers link their WhatsApp, customers order in plain chat, and Stallo turns those messages into orders, payments and deliveries.

FastAPI · PostgreSQL · RabbitMQ · Alembic · Python 3.12

> Team roles, workflow and conventions live in the org handbook: `stallo-hq/.github` → `HANDBOOK.md`.

## Architecture

One codebase, deployed as three processes:

| Process | Command | Does |
|---|---|---|
| `api` | `uvicorn app.main:app` | Webhooks, dashboard REST API |
| `inbound-worker` | `python -m workers.inbound_worker` | Parses inbound messages and payment events, runs the orchestrator |
| `outbound-worker` | `python -m workers.outbound_worker` | Sends WhatsApp replies at a paced rate |

```
WhatsApp provider ──► /webhooks/whatsapp ──► RabbitMQ (whatsapp.inbound) ──► inbound-worker
Paystack/Hubtel  ──► /webhooks/paystack ──► RabbitMQ (payments.inbound) ──┘     │
                                                                               ▼
                                     orchestrator ─► LLM ─► orders/inventory/payments/...
                                                                               │
                              RabbitMQ (whatsapp.outbound) ◄── notifications ◄─┘
                                       │
                                       ▼
                               outbound-worker ──► WhatsApp provider
```

### Layout

```
app/
  core/           config, logging
  db/             SQLAlchemy base, session, model registry (for Alembic)
  messaging/      RabbitMQ connection, queue + event names (the contract)
  modules/        one folder per domain; each has router / service / schemas / models
    ingestion/  sellers/  orchestrator/  conversations/
    orders/  inventory/  delivery/  payments/  exceptions/  notifications/
workers/          RabbitMQ consumers
alembic/          migrations
tests/
```

**Module rules**
- A router only calls its own module's `service.py`.
- Modules talk to each other through another module's `service.py` functions or through domain events. They never import another module's `models.py` directly.
- Queue and event names live only in `app/messaging/queues.py`.

## Getting started

```bash
cp .env.example .env
docker compose up -d postgres rabbitmq

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

alembic upgrade head
uvicorn app.main:app --reload          # http://localhost:8000/docs
python -m workers.inbound_worker       # in another terminal
python -m workers.outbound_worker      # in another terminal
```

Run the whole stack in containers: `docker compose --profile app up --build`
Add the WhatsApp provider: `docker compose --profile whatsapp up -d`

## Common tasks

```bash
pytest                                        # tests
ruff check . && ruff format .                 # lint + format
alembic revision --autogenerate -m "add orders table"
alembic upgrade head
```

The OpenAPI schema at `/openapi.json` is what `stallo-web` generates its API client from. A breaking change to it needs a heads-up to the frontend team.
