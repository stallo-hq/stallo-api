"""Filtering rules for inbound WhatsApp events."""

from app.modules.ingestion.schemas import WhatsAppWebhookEvent


def should_ingest(event: WhatsAppWebhookEvent) -> bool:
    """Drop the seller's own messages, group chats and empty events."""
    if event.from_me or event.is_group:
        return False
    return bool(event.text or event.media_url)
