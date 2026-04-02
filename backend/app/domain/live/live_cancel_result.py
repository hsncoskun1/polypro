"""Live order cancel result contract — v0.7.5."""
from dataclasses import dataclass
from app.domain.live.cancel_status import CancelStatus


@dataclass
class LiveCancelResult:
    cancel_allowed: bool
    cancel_status: CancelStatus
    reject_reason: str = ""
    retryable: bool = False
    terminal_failure: bool = False
    cancel_attempted_at: str = ""
