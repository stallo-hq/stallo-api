from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.modules.conversations.router import router as conversations_router
from app.modules.delivery.router import router as delivery_router
from app.modules.exceptions.router import router as exceptions_router
from app.modules.ingestion.router import router as ingestion_router
from app.modules.inventory.router import router as inventory_router
from app.modules.notifications.router import router as notifications_router
from app.modules.orders.router import router as orders_router
from app.modules.payments.router import router as payments_router
from app.modules.sellers.router import router as sellers_router

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="Stallo API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (
    ingestion_router,
    sellers_router,
    conversations_router,
    orders_router,
    inventory_router,
    payments_router,
    delivery_router,
    exceptions_router,
    notifications_router,
):
    app.include_router(r, prefix="/api/v1")


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
