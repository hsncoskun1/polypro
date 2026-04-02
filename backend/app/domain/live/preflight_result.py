"""Live execution preflight evaluation result — v0.7.2."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class PreflightResult:
    outbound_allowed: bool
    blocker_reasons: List[str] = field(default_factory=list)
