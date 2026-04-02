"""Release gate UI state — v0.8.5.

Maps release_ready and live_applied_testing_ready to UI-facing
status strings. Keeps the technical gate result separate from
how it is presented on the surface.
"""
from dataclasses import dataclass


@dataclass
class ReleaseGateUiState:
    """UI representation of the release + live test gate status.

    Attributes:
        release_status_label: Display label for release readiness (Turkish).
        live_gate_status_label: Display label for live test gate (Turkish).
        release_ready: Raw boolean forwarded from evaluator.
        live_applied_testing_ready: Raw boolean — never auto-True.
        live_mode_ui_blocked: True when live mode is not authorized for display.
    """
    release_status_label: str = ""
    live_gate_status_label: str = ""
    release_ready: bool = False
    live_applied_testing_ready: bool = False
    live_mode_ui_blocked: bool = True
