"""Admin surface view — v0.8.5.

Admin-facing surface view. Admin has broader visibility than the
user-facing surface: full operational control state, blocked trade/rule/
risk events, execution fills, claim events and operational alerts.

Secrets and credential fields are never included.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class AdminSurfaceView:
    """Admin-facing surface view model.

    Attributes:
        launcher_blocked: Whether app access is blocked at launcher level.
        backend_ready: Backend readiness status.
        release_ready: Release readiness status.
        live_applied_testing_ready: Live test gate status.
        admin_report_snapshot_summary: High-level summary of admin report.
        visible_panels: List of panel names visible to admin (superset of user panels).
        admin_surface_labels_tr: Turkish labels for admin surface.
        blocked_reason_messages: Turkish messages for any active blocks.
        safe_stop_active: Whether safe stop is currently active.
        scheduler_enabled: Whether the scheduler is enabled.
        global_disable_active: Whether global disable is active.
        operational_alerts: Current operational alerts.
    """
    launcher_blocked: bool = True
    backend_ready: bool = False
    release_ready: bool = False
    live_applied_testing_ready: bool = False
    admin_report_snapshot_summary: str = ""
    visible_panels: List[str] = field(default_factory=list)
    admin_surface_labels_tr: dict = field(default_factory=dict)
    blocked_reason_messages: List[str] = field(default_factory=list)
    safe_stop_active: bool = False
    scheduler_enabled: bool = True
    global_disable_active: bool = False
    operational_alerts: List[str] = field(default_factory=list)
