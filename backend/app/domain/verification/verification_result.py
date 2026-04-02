"""Verification gate result model.

Output of the verification gate evaluation. trade_allowed is True only when
all mandatory checks pass. Fail-closed: any blocker → trade denied.
This result is independent of strategy entry decision.
"""
from dataclasses import dataclass, field


@dataclass
class VerificationResult:
    """Outcome of a verification gate evaluation."""
    trade_allowed: bool
    blocker_reasons: list[str] = field(default_factory=list)
