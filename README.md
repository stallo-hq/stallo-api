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
uvicorn app.main:app --reload          # http://localhost:8000/api/v1/docs
python -m workers.inbound_worker       # in another terminal
python -m workers.outbound_worker      # in another terminal
```

Run the whole stack in containers: `docker compose --profile app up --build`
Add the WhatsApp provider: `docker compose --profile whatsapp up -d`

## API versioning

Every endpoint lives under a version prefix: `/api/v1/...`. Only `/health` is unversioned.

```
app/api/v1/router.py   # mounts every module router under /api/v1
app/modules/*/router.py  # declares paths without a version, e.g. /orders
```

- OpenAPI schema: `/api/v1/openapi.json` · interactive docs: `/api/v1/docs`
- Payment and WhatsApp webhooks are versioned too (`/api/v1/webhooks/...`). Configure the providers with the full path.

**What counts as breaking (needs a new version):** removing or renaming an endpoint or field, changing a field's type or meaning, making an optional request field required, changing status codes or error shapes.

**Not breaking (stays in v1):** new endpoints, new optional request fields, new response fields.

**Introducing v2:**
1. Add `app/api/v2/router.py` and mount it in `app/main.py` under `/api/v2`.
2. Put the changed endpoints in `router_v2.py` and `schemas_v2.py` inside the affected module. Unchanged endpoints can be included in both versions.
3. Keep v1 running until `stallo-web` and every webhook provider have moved to v2, then remove it in a separate PR.
4. Version changes are contract changes (handbook §3.4) and need sign-off from the leads.

## Common tasks

```bash
pytest                                        # tests
ruff check . && ruff format .                 # lint + format
alembic revision --autogenerate -m "add orders table"
alembic upgrade head
```

The OpenAPI schema at `/api/v1/openapi.json` is what `stallo-web` generates its API client from. A breaking change to it needs a heads-up to the frontend team.
