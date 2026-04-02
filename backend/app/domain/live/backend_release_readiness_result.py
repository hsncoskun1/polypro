"""Backend release readiness result — v0.8.4."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class BackendReleaseReadinessResult:
    """Result of backend release readiness evaluation.

    Attributes:
        release_ready: True only when all critical chain links pass.
        blocker_reasons: Ordered list of reason codes for missing links.
    """
    release_ready: bool = False
    blocker_reasons: List[str] = field(default_factory=list)
