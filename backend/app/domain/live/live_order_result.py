"""Live order submission result contract — v0.7.3."""
from dataclasses import dataclass, field
from typing import Optional
from app.domain.live.order_submission_status import OrderSubmissionStatus


@dataclass
class LiveOrderResult:
    submission_allowed: bool
    order_submission_status: OrderSubmissionStatus

    # Present when submission was attempted
    order_id: str = ""
    reject_reason: str = ""

    # Failure classification
    retryable: bool = False
    terminal_failure: bool = False

    # Audit
    submit_attempted_at: str = ""
