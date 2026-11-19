"""Normalized webhook payload. Provider-specific shapes are mapped into this."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WhatsAppWebhookEvent(BaseModel):
    seller_session_id: str = Field(description="Linked-device session that received the message")
    chat_id: str
    sender: str
    from_me: bool = False
    is_group: bool = False
    message_id: str
    text: str | None = None
    media_url: str | None = None
    timestamp: datetime
    raw: dict[str, Any] = Field(default_factory=dict)
