"""Outbound action type enum — v0.7.2."""
from enum import Enum


class OutboundActionType(str, Enum):
    LIVE_ORDER_SUBMIT = "live_order_submit"
    LIVE_ORDER_CANCEL = "live_order_cancel"
    LIVE_CLAIM_SUBMIT = "live_claim_submit"
    OTHER_LIVE_OUTBOUND = "other_live_outbound"
