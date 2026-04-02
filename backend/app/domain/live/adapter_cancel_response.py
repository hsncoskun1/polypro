"""Adapter cancel response contract — v0.7.8."""
from dataclasses import dataclass
from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus


@dataclass
class AdapterCancelResponse:
    order_id: str
    outcome_status: AdapterOutcomeStatus
    reject_reason: str = ""
    retryable: bool = False
    terminal_failure: bool = False
