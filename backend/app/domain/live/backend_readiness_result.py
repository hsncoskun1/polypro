"""Backend readiness result — v0.8.2.

Produced by BackendReadinessEvaluator. Carries the overall backend_ready
flag plus a list of every blocker that prevented readiness.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class BackendReadinessResult:
    """Result of evaluating the end-to-end live backend readiness context.

    Attributes:
        backend_ready: True only when every critical chain link is present.
        blocker_reasons: Ordered list of reason codes for missing links.
        client_mode: Forwarded from the context for traceability.
    """
    backend_ready: bool = False
    blocker_reasons: List[str] = field(default_factory=list)
    client_mode: str = ""
