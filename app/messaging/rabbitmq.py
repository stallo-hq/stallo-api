import json
from typing import Any

import aio_pika

from app.core.config import get_settings
from app.messaging import queues


async def connect() -> aio_pika.abc.AbstractRobustConnection:
    return await aio_pika.connect_robust(get_settings().rabbitmq_url)


async def declare_topology(channel: aio_pika.abc.AbstractChannel) -> aio_pika.abc.AbstractExchange:
    exchange = await channel.declare_exchange(
        queues.EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True
    )
    for name in (
        queues.INBOUND_WHATSAPP,
        queues.INBOUND_PAYMENTS,
        queues.OUTBOUND_WHATSAPP,
        queues.DOMAIN_EVENTS,
    ):
        queue = await channel.declare_queue(name, durable=True)
        await queue.bind(exchange, routing_key=name)
    domain = await channel.get_queue(queues.DOMAIN_EVENTS)
    await domain.bind(exchange, routing_key="order.#")
    await domain.bind(exchange, routing_key="payment.#")
    await domain.bind(exchange, routing_key="inventory.#")
    await domain.bind(exchange, routing_key="exception.#")
    return exchange


async def publish(routing_key: str, payload: dict[str, Any]) -> None:
    connection = await connect()
    async with connection:
        channel = await connection.channel()
        exchange = await declare_topology(channel)
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
