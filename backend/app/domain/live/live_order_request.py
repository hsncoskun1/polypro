"""Live order submission request contract — v0.7.3.

Carries the intent and guard results for a live order submission.
No network calls. Seam only.
"""
from dataclasses import dataclass


@dataclass
class LiveOrderRequest:
    # Market / trade intent
    event_key: str
    market_id: str
    side: str
    requested_size: float
    limit_price: float

    # Guard results from upstream evaluators
    live_mode_requested: bool
    preflight_passed: bool
    outbound_allowed: bool
