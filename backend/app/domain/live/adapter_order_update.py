"""Adapter order update model — v0.7.8.

Read model for fill/status updates fetched or streamed from exchange adapter.
"""
from dataclasses import dataclass
from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus


@dataclass
class AdapterOrderUpdate:
    order_id: str
    outcome_status: AdapterOutcomeStatus
    filled_size: float = 0.0
    remaining_size: float = 0.0
    update_timestamp: str = ""
