"""Consumes inbound WhatsApp and payment events and hands them to the orchestrator.

Run: python -m workers.inbound_worker
Owner: R2 (WhatsApp path) / R4 (payments path)
"""

import asyncio
import json

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.messaging import queues
from app.messaging.rabbitmq import connect, declare_topology

log = get_logger(__name__)


async def handle_whatsapp(payload: dict) -> None:
    # TODO(R2): orchestrator.service.handle_inbound_message(payload)
    log.info("whatsapp.inbound", chat_id=payload.get("chat_id"))


async def handle_payment(payload: dict) -> None:
    # TODO(R4): payments.service.handle_provider_event(payload)
    log.info("payments.inbound", provider=payload.get("provider"))


async def main() -> None:
    configure_logging(get_settings().log_level)
    connection = await connect()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    await declare_topology(channel)

    async def consume(queue_name: str, handler) -> None:
        queue = await channel.get_queue(queue_name)
        async with queue.iterator() as it:
            async for message in it:
                async with message.process(requeue=False):
                    await handler(json.loads(message.body))

    await asyncio.gather(
        consume(queues.INBOUND_WHATSAPP, handle_whatsapp),
        consume(queues.INBOUND_PAYMENTS, handle_payment),
    )


if __name__ == "__main__":
    asyncio.run(main())
