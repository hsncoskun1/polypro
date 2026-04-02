"""Backend final validation result — v0.8.3."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class BackendFinalValidationResult:
    """Result of validate_backend_final_state().

    Attributes:
        final_backend_ready: True only when all critical non-live chain links pass.
        live_applied_testing_ready: Always False in this pack — live applied testing
            is a separate authorization step, never auto-enabled by validation.
        blocker_reasons: Ordered list of reason codes for failed chain links.
        validation_mode: Forwarded from context for traceability.
    """
    final_backend_ready: bool = False
    live_applied_testing_ready: bool = False
    blocker_reasons: List[str] = field(default_factory=list)
    validation_mode: str = ""
