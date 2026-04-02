"""Launcher readiness result model.

Output of readiness evaluation. access_allowed is True only when
all mandatory conditions are met. Fail-closed: any blocker → access denied.
"""
from dataclasses import dataclass, field


@dataclass
class ReadinessResult:
    """Outcome of a readiness evaluation."""
    access_allowed: bool
    blocker_reasons: list[str] = field(default_factory=list)
