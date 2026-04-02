"""Live order replace result contract — v0.7.5."""
from dataclasses import dataclass
from app.domain.live.replace_status import ReplaceStatus


@dataclass
class LiveReplaceResult:
    replace_allowed: bool
    replace_status: ReplaceStatus
    replace_reason: str = ""
    retryable: bool = False
    terminal_failure: bool = False
    replace_attempted_at: str = ""
