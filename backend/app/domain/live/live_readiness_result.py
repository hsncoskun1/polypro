"""Live readiness evaluation output contract — v0.7.0."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class LiveReadinessResult:
    live_ready: bool
    blocker_reasons: List[str] = field(default_factory=list)
