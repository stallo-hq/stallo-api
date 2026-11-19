"""Sends queued WhatsApp replies at a paced rate to avoid number bans.

Run: python -m workers.outbound_worker
Owner: R4 Payments & Notifications
"""

import asyncio
import json

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.messaging import queues
from app.messaging.rabbitmq import connect, declare_topology

log = get_logger(__name__)


async def send(payload: dict) -> None:
    # TODO(R1): call the linked-device API client (Evolution API / WAHA)
    log.info("whatsapp.outbound", chat_id=payload.get("chat_id"))


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    delay = 1 / settings.outbound_rate_per_second
    connection = await connect()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    await declare_topology(channel)
    queue = await channel.get_queue(queues.OUTBOUND_WHATSAPP)
    async with queue.iterator() as it:
        async for message in it:
            async with message.process():
                await send(json.loads(message.body))
                await asyncio.sleep(delay)


if __name__ == "__main__":
    asyncio.run(main())
