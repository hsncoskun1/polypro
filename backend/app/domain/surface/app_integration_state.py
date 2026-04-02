"""App integration state — v0.8.5.

Combines launcher readiness, backend readiness and live test gate results
into a single surface-facing integration state. This is the entry point
for assembling any user or admin surface view.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class AppIntegrationState:
    """Surface-level integration state aggregating all readiness layers.

    Attributes:
        launcher_blocked: Launcher readiness has NOT been confirmed.
            If True, user cannot meaningfully use the application.
        backend_ready: v0.8.2 end-to-end backend readiness passed.
        final_backend_ready: v0.8.3 final non-live validation passed.
        release_ready: v0.8.4 backend release readiness passed.
        live_applied_testing_ready: v0.8.4 live test gate passed.
            Always a separate gate — never derived from release_ready alone.
        live_mode_active: Live mode is currently active.
        blocked_reasons: List of reason codes for any active blocks.
    """
    launcher_blocked: bool = True
    backend_ready: bool = False
    final_backend_ready: bool = False
    release_ready: bool = False
    live_applied_testing_ready: bool = False
    live_mode_active: bool = False
    blocked_reasons: List[str] = field(default_factory=list)
