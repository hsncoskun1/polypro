"""RiskResult — output of risk engine evaluation."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class RiskResult:
    risk_allowed: bool
    blocker_reasons: List[str] = field(default_factory=list)
