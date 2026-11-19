"""Assembles every module router into the v1 API.

All v1 endpoints are mounted under `settings.api_v1_prefix` (default `/api/v1`) in `app/main.py`.
A module's router only declares its own path (e.g. `/orders`); the version comes from here.
"""

from fastapi import APIRouter

from app.modules.conversations.router import router as conversations_router
from app.modules.delivery.router import router as delivery_router
from app.modules.exceptions.router import router as exceptions_router
from app.modules.ingestion.router import router as ingestion_router
from app.modules.inventory.router import router as inventory_router
from app.modules.notifications.router import router as notifications_router
from app.modules.orders.router import router as orders_router
from app.modules.payments.router import router as payments_router
from app.modules.sellers.router import router as sellers_router

api_router = APIRouter()

for module_router in (
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
    api_router.include_router(module_router)
