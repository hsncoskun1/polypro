"""Live test gate result — v0.8.4.

live_applied_testing_ready=True only when every gate condition passes.
It is NEVER auto-set based on release_ready alone.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class LiveTestGateResult:
    """Result of live test gate evaluation.

    Attributes:
        live_applied_testing_ready: True only when all gate conditions pass.
            Never auto-enabled — requires explicit gate authorization.
        blocker_reasons: Ordered list of reason codes for gate failures.
    """
    live_applied_testing_ready: bool = False
    blocker_reasons: List[str] = field(default_factory=list)
