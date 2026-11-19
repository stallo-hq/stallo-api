import hashlib
import hmac

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.core.config import get_settings
from app.messaging import queues
from app.messaging.rabbitmq import publish
from app.modules.ingestion.schemas import WhatsAppWebhookEvent
from app.modules.ingestion.service import should_ingest

router = APIRouter(prefix="/webhooks", tags=["ingestion"])


@router.post("/whatsapp", status_code=status.HTTP_202_ACCEPTED)
async def whatsapp_webhook(
    event: WhatsAppWebhookEvent,
    x_webhook_secret: str | None = Header(default=None),
) -> dict[str, str]:
    """Receives events from the linked-device provider (Evolution API / WAHA).

    Responds fast and pushes to RabbitMQ; all processing happens in workers.
    """
    expected = get_settings().whatsapp_webhook_secret
    if expected and not hmac.compare_digest(x_webhook_secret or "", expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid webhook secret")
    if not should_ingest(event):
        return {"status": "ignored"}
    await publish(queues.INBOUND_WHATSAPP, event.model_dump(mode="json"))
    return {"status": "queued"}


@router.post("/paystack", status_code=status.HTTP_202_ACCEPTED)
async def paystack_webhook(
    request: Request,
    x_paystack_signature: str = Header(...),
) -> dict[str, str]:
    """Paystack signs the raw body with HMAC-SHA512 using the secret key."""
    body = await request.body()
    secret = get_settings().paystack_secret_key.encode()
    digest = hmac.new(secret, body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(digest, x_paystack_signature):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid signature")
    await publish(queues.INBOUND_PAYMENTS, {"provider": "paystack", "raw": body.decode()})
    return {"status": "queued"}


@router.post("/hubtel", status_code=status.HTTP_202_ACCEPTED)
async def hubtel_webhook(request: Request) -> dict[str, str]:
    """TODO(R4): validate Hubtel callback per their docs before trusting it."""
    body = await request.body()
    await publish(queues.INBOUND_PAYMENTS, {"provider": "hubtel", "raw": body.decode()})
    return {"status": "queued"}
