"""Adapter submit response contract — v0.7.8."""
from dataclasses import dataclass
from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus


@dataclass
class AdapterSubmitResponse:
    order_id: str
    outcome_status: AdapterOutcomeStatus
    exchange_order_id: str = ""
    reject_reason: str = ""
    retryable: bool = False
    terminal_failure: bool = False
