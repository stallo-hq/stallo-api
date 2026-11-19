"""Single source of truth for queue and event names.

Changing a name here is a contract change: tag every consumer's owner on the PR (see handbook §3.4).
"""

EXCHANGE = "stallo.events"

# Queues
INBOUND_WHATSAPP = "whatsapp.inbound"  # raw messages from the webhook receiver
INBOUND_PAYMENTS = "payments.inbound"  # validated payment provider events
OUTBOUND_WHATSAPP = "whatsapp.outbound"  # replies to send, paced by the outbound worker
DOMAIN_EVENTS = "domain.events"  # order.created, payment.confirmed, ...

# Domain event routing keys
ORDER_CREATED = "order.created"
ORDER_STATUS_CHANGED = "order.status_changed"
PAYMENT_CONFIRMED = "payment.confirmed"
PAYMENT_FAILED = "payment.failed"
STOCK_LOW = "inventory.stock_low"
EXCEPTION_RAISED = "exception.raised"
