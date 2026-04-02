"""Adapter cancel request contract — v0.7.8."""
from dataclasses import dataclass


@dataclass
class AdapterCancelRequest:
    order_id: str
    event_key: str
