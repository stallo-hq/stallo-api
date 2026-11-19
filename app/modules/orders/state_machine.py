"""Explicit order state machine. All status changes go through `transition`."""

from enum import StrEnum


class OrderStatus(StrEnum):
    DRAFT = "draft"  # being assembled in a conversation
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CREATED = "created"  # customer confirmed
    PAID = "paid"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


ALLOWED: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {OrderStatus.AWAITING_CONFIRMATION, OrderStatus.CANCELLED},
    OrderStatus.AWAITING_CONFIRMATION: {
        OrderStatus.CREATED,
        OrderStatus.DRAFT,
        OrderStatus.CANCELLED,
    },
    OrderStatus.CREATED: {OrderStatus.PAID, OrderStatus.DISPATCHED, OrderStatus.CANCELLED},
    OrderStatus.PAID: {OrderStatus.DISPATCHED, OrderStatus.CANCELLED},
    OrderStatus.DISPATCHED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


class InvalidTransitionError(ValueError):
    pass


def transition(current: OrderStatus, target: OrderStatus) -> OrderStatus:
    if target not in ALLOWED[current]:
        raise InvalidTransitionError(f"cannot move order from {current} to {target}")
    return target
