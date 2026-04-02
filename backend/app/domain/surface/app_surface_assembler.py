"""App surface assembler — v0.8.5.

Assembles AppSurfaceView (user) and AdminSurfaceView (admin) from
AppIntegrationState and the existing backend domain snapshots.

Design rules:
- launcher_blocked=True limits visible panels and sets blocked messages.
- User surface never contains admin-only data.
- Secrets are never included in any surface view.
- release_ready and live_applied_testing_ready are always shown separately.
- Turkish labels are applied via surface_label_mapper.
"""
from typing import List

from app.domain.surface.app_integration_state import AppIntegrationState
from app.domain.surface.app_surface_view import AppSurfaceView
from app.domain.surface.admin_surface_view import AdminSurfaceView
from app.domain.surface.release_gate_ui_state import ReleaseGateUiState
from app.domain.surface.surface_label_mapper import (
    USER_SURFACE_LABELS_TR,
    ADMIN_SURFACE_LABELS_TR,
    USER_VISIBLE_PANELS,
    ADMIN_VISIBLE_PANELS,
    get_blocked_reason_message_tr,
)


def _build_release_gate_ui_state(state: AppIntegrationState) -> ReleaseGateUiState:
    return ReleaseGateUiState(
        release_status_label=(
            "Yayın Hazır" if state.release_ready else "Yayın Hazır Değil"
        ),
        live_gate_status_label=(
            "Canlı Test Kapısı Açık" if state.live_applied_testing_ready
            else "Canlı Test Kapısı Kapalı"
        ),
        release_ready=state.release_ready,
        live_applied_testing_ready=state.live_applied_testing_ready,
        live_mode_ui_blocked=not state.live_applied_testing_ready,
    )


def _build_blocked_messages(state: AppIntegrationState) -> List[str]:
    messages = []
    if state.launcher_blocked:
        messages.append(get_blocked_reason_message_tr("launcher_blocked"))
    for reason in state.blocked_reasons:
        messages.append(get_blocked_reason_message_tr(reason))
    return messages


def assemble_user_surface(
    state: AppIntegrationState,
    open_positions: List[str] = None,
    closed_positions: List[str] = None,
    balance_summary: str = "",
    pnl_summary: str = "",
    claim_summary: str = "",
) -> AppSurfaceView:
    """Assemble the user-facing surface view.

    When launcher_blocked=True, visible_panels is empty and
    blocked_reason_messages are populated.
    """
    gate_ui = _build_release_gate_ui_state(state)
    blocked_msgs = _build_blocked_messages(state)

    if state.launcher_blocked:
        visible = []
    else:
        visible = list(USER_VISIBLE_PANELS)

    return AppSurfaceView(
        launcher_blocked=state.launcher_blocked,
        open_positions_view=open_positions or [],
        closed_positions_view=closed_positions or [],
        balance_summary_view=balance_summary,
        pnl_summary_view=pnl_summary,
        claim_summary_view=claim_summary,
        visible_panels=visible,
        release_gate_ui_state=gate_ui,
        user_surface_labels_tr=dict(USER_SURFACE_LABELS_TR),
        blocked_reason_messages=blocked_msgs,
    )


def assemble_admin_surface(
    state: AppIntegrationState,
    admin_report_summary: str = "",
    safe_stop_active: bool = False,
    scheduler_enabled: bool = True,
    global_disable_active: bool = False,
    operational_alerts: List[str] = None,
) -> AdminSurfaceView:
    """Assemble the admin-facing surface view.

    Admin always sees the full panel set regardless of launcher_blocked —
    but blocked_reason_messages and launcher_blocked flag are forwarded.
    """
    blocked_msgs = _build_blocked_messages(state)

    return AdminSurfaceView(
        launcher_blocked=state.launcher_blocked,
        backend_ready=state.backend_ready,
        release_ready=state.release_ready,
        live_applied_testing_ready=state.live_applied_testing_ready,
        admin_report_snapshot_summary=admin_report_summary,
        visible_panels=list(ADMIN_VISIBLE_PANELS),
        admin_surface_labels_tr=dict(ADMIN_SURFACE_LABELS_TR),
        blocked_reason_messages=blocked_msgs,
        safe_stop_active=safe_stop_active,
        scheduler_enabled=scheduler_enabled,
        global_disable_active=global_disable_active,
        operational_alerts=operational_alerts or [],
    )
