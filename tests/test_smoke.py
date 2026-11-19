from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.ingestion.schemas import WhatsAppWebhookEvent
from app.modules.ingestion.service import should_ingest
from app.modules.orders.state_machine import InvalidTransitionError, OrderStatus, transition

client = TestClient(app)


def test_health() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def _event(**kw) -> WhatsAppWebhookEvent:
    base = dict(
        seller_session_id="s1",
        chat_id="c1",
        sender="233200000000",
        message_id="m1",
        text="2 bags of rice",
        timestamp=datetime.now(UTC),
    )
    return WhatsAppWebhookEvent(**(base | kw))


def test_filters_self_and_group_messages() -> None:
    assert should_ingest(_event())
    assert not should_ingest(_event(from_me=True))
    assert not should_ingest(_event(is_group=True))
    assert not should_ingest(_event(text=None))


def test_order_state_machine() -> None:
    assert transition(OrderStatus.CREATED, OrderStatus.PAID) == OrderStatus.PAID
    with pytest.raises(InvalidTransitionError):
        transition(OrderStatus.DELIVERED, OrderStatus.CREATED)
