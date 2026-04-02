"""Tests for frontend/launcher surface wiring + final app integration — v0.8.5."""
from app.domain.surface.app_integration_state import AppIntegrationState
from app.domain.surface.release_gate_ui_state import ReleaseGateUiState
from app.domain.surface.app_surface_view import AppSurfaceView
from app.domain.surface.admin_surface_view import AdminSurfaceView
from app.domain.surface.surface_label_mapper import (
    USER_SURFACE_LABELS_TR,
    ADMIN_SURFACE_LABELS_TR,
    USER_VISIBLE_PANELS,
    ADMIN_VISIBLE_PANELS,
    BLOCKED_REASON_MESSAGES_TR,
    get_blocked_reason_message_tr,
)
from app.domain.surface.app_surface_assembler import (
    assemble_user_surface,
    assemble_admin_surface,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ready_state(**overrides) -> AppIntegrationState:
    defaults = dict(
        launcher_blocked=False,
        backend_ready=True,
        final_backend_ready=True,
        release_ready=True,
        live_applied_testing_ready=False,  # separate gate — not auto-True
        live_mode_active=False,
        blocked_reasons=[],
    )
    defaults.update(overrides)
    return AppIntegrationState(**defaults)


# ---------------------------------------------------------------------------
# TestAppIntegrationState
# ---------------------------------------------------------------------------

class TestAppIntegrationState:
    def test_defaults_blocked(self):
        """Default state is maximally blocked (fail-closed)."""
        s = AppIntegrationState()
        assert s.launcher_blocked is True
        assert s.backend_ready is False
        assert s.final_backend_ready is False
        assert s.release_ready is False
        assert s.live_applied_testing_ready is False
        assert s.live_mode_active is False
        assert s.blocked_reasons == []

    def test_all_fields_settable(self):
        s = _ready_state()
        assert s.launcher_blocked is False
        assert s.backend_ready is True
        assert s.release_ready is True

    def test_blocked_reasons_independent(self):
        s1 = AppIntegrationState()
        s2 = AppIntegrationState()
        s1.blocked_reasons.append("x")
        assert s2.blocked_reasons == []


# ---------------------------------------------------------------------------
# TestReleaseGateUiState
# ---------------------------------------------------------------------------

class TestReleaseGateUiState:
    def test_defaults(self):
        ui = ReleaseGateUiState()
        assert ui.release_ready is False
        assert ui.live_applied_testing_ready is False
        assert ui.live_mode_ui_blocked is True
        assert ui.release_status_label == ""
        assert ui.live_gate_status_label == ""

    def test_live_mode_ui_blocked_when_not_ready(self):
        ui = ReleaseGateUiState(live_applied_testing_ready=False)
        assert ui.live_mode_ui_blocked is True


# ---------------------------------------------------------------------------
# TestSurfaceLabelMapper
# ---------------------------------------------------------------------------

class TestSurfaceLabelMapper:
    def test_user_labels_tr_exist(self):
        assert "open_positions" in USER_SURFACE_LABELS_TR
        assert USER_SURFACE_LABELS_TR["open_positions"] == "Açık Pozisyonlar"

    def test_admin_labels_tr_superset_of_user(self):
        for key in USER_SURFACE_LABELS_TR:
            assert key in ADMIN_SURFACE_LABELS_TR

    def test_admin_labels_tr_has_extra_keys(self):
        assert "safe_stop" in ADMIN_SURFACE_LABELS_TR
        assert "admin_report" in ADMIN_SURFACE_LABELS_TR
        assert "safe_stop" not in USER_SURFACE_LABELS_TR

    def test_blocked_reason_messages_tr_exist(self):
        assert "launcher_blocked" in BLOCKED_REASON_MESSAGES_TR
        assert "live_mode_not_authorized" in BLOCKED_REASON_MESSAGES_TR

    def test_blocked_messages_are_turkish(self):
        msg = BLOCKED_REASON_MESSAGES_TR["launcher_blocked"]
        assert len(msg) > 0

    def test_get_blocked_reason_message_known(self):
        msg = get_blocked_reason_message_tr("launcher_blocked")
        assert "Başlatıcı" in msg

    def test_get_blocked_reason_message_unknown_fallback(self):
        msg = get_blocked_reason_message_tr("unknown_xyz")
        assert "unknown_xyz" in msg

    def test_user_visible_panels(self):
        assert "open_positions" in USER_VISIBLE_PANELS
        assert "balance_summary" in USER_VISIBLE_PANELS
        assert "safe_stop" not in USER_VISIBLE_PANELS

    def test_admin_visible_panels_superset(self):
        for p in USER_VISIBLE_PANELS:
            assert p in ADMIN_VISIBLE_PANELS
        assert "safe_stop" in ADMIN_VISIBLE_PANELS
        assert "admin_report" in ADMIN_VISIBLE_PANELS


# ---------------------------------------------------------------------------
# TestUserSurface — assemble_user_surface
# ---------------------------------------------------------------------------

class TestUserSurfaceAssembler:
    def test_launcher_blocked_empties_visible_panels(self):
        state = AppIntegrationState(launcher_blocked=True)
        view = assemble_user_surface(state)
        assert view.launcher_blocked is True
        assert view.visible_panels == []

    def test_launcher_not_blocked_shows_panels(self):
        state = _ready_state()
        view = assemble_user_surface(state)
        assert view.launcher_blocked is False
        assert len(view.visible_panels) > 0
        assert "open_positions" in view.visible_panels

    def test_user_surface_contains_control_plane_data(self):
        state = _ready_state()
        view = assemble_user_surface(
            state,
            open_positions=["pos_001"],
            balance_summary="Bakiye: 1000 USDC",
            pnl_summary="Kar/Zarar: +50 USDC",
            claim_summary="Hak Talebi: 0",
        )
        assert view.open_positions_view == ["pos_001"]
        assert "1000" in view.balance_summary_view
        assert "50" in view.pnl_summary_view

    def test_user_surface_has_turkish_labels(self):
        view = assemble_user_surface(_ready_state())
        assert "open_positions" in view.user_surface_labels_tr
        assert view.user_surface_labels_tr["open_positions"] == "Açık Pozisyonlar"

    def test_user_surface_no_admin_fields(self):
        view = assemble_user_surface(_ready_state())
        assert not hasattr(view, "safe_stop_active")
        assert not hasattr(view, "blocked_trades")
        assert not hasattr(view, "operational_alerts")

    def test_release_gate_ui_state_built(self):
        state = _ready_state(release_ready=True, live_applied_testing_ready=False)
        view = assemble_user_surface(state)
        assert view.release_gate_ui_state is not None
        assert view.release_gate_ui_state.release_ready is True
        assert view.release_gate_ui_state.live_applied_testing_ready is False
        assert view.release_gate_ui_state.live_mode_ui_blocked is True

    def test_blocked_reason_messages_when_launcher_blocked(self):
        state = AppIntegrationState(launcher_blocked=True)
        view = assemble_user_surface(state)
        assert len(view.blocked_reason_messages) > 0
        assert any("Başlatıcı" in msg for msg in view.blocked_reason_messages)

    def test_returns_app_surface_view_type(self):
        view = assemble_user_surface(_ready_state())
        assert isinstance(view, AppSurfaceView)

    def test_live_mode_not_ready_ui_blocked(self):
        state = _ready_state(live_applied_testing_ready=False)
        view = assemble_user_surface(state)
        assert view.release_gate_ui_state.live_mode_ui_blocked is True

    def test_release_ready_and_live_gate_shown_separately(self):
        state = _ready_state(release_ready=True, live_applied_testing_ready=False)
        view = assemble_user_surface(state)
        gate = view.release_gate_ui_state
        assert gate.release_ready is True
        assert gate.live_applied_testing_ready is False


# ---------------------------------------------------------------------------
# TestAdminSurface — assemble_admin_surface
# ---------------------------------------------------------------------------

class TestAdminSurfaceAssembler:
    def test_admin_sees_full_panels(self):
        state = _ready_state()
        view = assemble_admin_surface(state)
        assert "safe_stop" in view.visible_panels
        assert "admin_report" in view.visible_panels
        assert "backend_readiness" in view.visible_panels

    def test_admin_has_broader_panels_than_user(self):
        state = _ready_state()
        user_view = assemble_user_surface(state)
        admin_view = assemble_admin_surface(state)
        assert len(admin_view.visible_panels) > len(user_view.visible_panels)

    def test_admin_surface_has_turkish_labels(self):
        view = assemble_admin_surface(_ready_state())
        assert "safe_stop" in view.admin_surface_labels_tr
        assert view.admin_surface_labels_tr["safe_stop"] == "Güvenli Durdurma"

    def test_admin_has_backend_ready_field(self):
        state = _ready_state(backend_ready=True)
        view = assemble_admin_surface(state)
        assert view.backend_ready is True

    def test_admin_release_and_gate_shown_separately(self):
        state = _ready_state(release_ready=True, live_applied_testing_ready=False)
        view = assemble_admin_surface(state)
        assert view.release_ready is True
        assert view.live_applied_testing_ready is False

    def test_admin_blocked_reasons_forwarded(self):
        state = AppIntegrationState(
            launcher_blocked=True,
            blocked_reasons=["backend_not_ready"],
        )
        view = assemble_admin_surface(state)
        assert len(view.blocked_reason_messages) >= 2

    def test_admin_safe_stop_state_forwarded(self):
        view = assemble_admin_surface(_ready_state(), safe_stop_active=True)
        assert view.safe_stop_active is True

    def test_admin_operational_alerts_forwarded(self):
        view = assemble_admin_surface(
            _ready_state(),
            operational_alerts=["alert_001"],
        )
        assert "alert_001" in view.operational_alerts

    def test_returns_admin_surface_view_type(self):
        view = assemble_admin_surface(_ready_state())
        assert isinstance(view, AdminSurfaceView)

    def test_admin_report_summary_forwarded(self):
        view = assemble_admin_surface(
            _ready_state(),
            admin_report_summary="Rapor özeti",
        )
        assert view.admin_report_snapshot_summary == "Rapor özeti"

    def test_secrets_not_in_admin_surface(self):
        """Admin surface never contains credential or secret fields."""
        view = assemble_admin_surface(_ready_state())
        view_dict = view.__dict__
        sensitive = {"api_key", "api_secret", "private_key", "passphrase", "signature"}
        for field_name in view_dict:
            assert field_name not in sensitive
