"""Live order event type enum — v0.7.6."""
from enum import Enum


class LiveOrderEventType(str, Enum):
    ORDER_SUBMITTED = "order_submitted"
    ORDER_ACCEPTED = "order_accepted"
    ORDER_PARTIALLY_FILLED = "order_partially_filled"
    ORDER_FILLED = "order_filled"
    ORDER_CANCEL_REQUESTED = "order_cancel_requested"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_REPLACE_REQUESTED = "order_replace_requested"
    ORDER_REPLACED = "order_replaced"
    ORDER_REJECTED = "order_rejected"
    ORDER_EXPIRED = "order_expired"
    ORDER_FAILED = "order_failed"
