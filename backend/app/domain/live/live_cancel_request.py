"""Live order cancel request contract — v0.7.5."""
from dataclasses import dataclass


@dataclass
class LiveCancelRequest:
    order_id: str
    outbound_allowed: bool
    preflight_passed: bool
