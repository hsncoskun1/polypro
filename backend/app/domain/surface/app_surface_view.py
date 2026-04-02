"""App surface view — v0.8.5.

User-facing surface view. Contains only the data a regular user
can see. Admin-only data (blocked trades, risk events, alerts) is
not present here.

Secrets and sensitive credential fields are never included.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class AppSurfaceView:
    """User-facing surface view model.

    Attributes:
        launcher_blocked: Whether app access is blocked at launcher level.
        open_positions_view: List of open position summary strings.
        closed_positions_view: List of closed position summary strings.
        balance_summary_view: Balance summary string for display.
        pnl_summary_view: PnL summary string for display.
        claim_summary_view: Claim/settlement summary string.
        visible_panels: List of panel names visible to this user.
        release_gate_ui_state: Release and live gate UI status.
        user_surface_labels_tr: Turkish labels for this surface.
        blocked_reason_messages: Turkish messages for any active blocks.
    """
    launcher_blocked: bool = True
    open_positions_view: List[str] = field(default_factory=list)
    closed_positions_view: List[str] = field(default_factory=list)
    balance_summary_view: str = ""
    pnl_summary_view: str = ""
    claim_summary_view: str = ""
    visible_panels: List[str] = field(default_factory=list)
    release_gate_ui_state: "ReleaseGateUiState | None" = None  # type: ignore[name-defined]
    user_surface_labels_tr: dict = field(default_factory=dict)
    blocked_reason_messages: List[str] = field(default_factory=list)
