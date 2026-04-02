"""Tests for admin operational control + reporting pack — v0.6.2."""
from app.domain.admin.admin_control import AdminControl
from app.domain.admin.admin_report_snapshot import AdminReportSnapshot
from app.domain.admin.admin_report_assembler import assemble_admin_report_snapshot
from app.domain.admin.admin_label_map import ADMIN_TURKISH_LABELS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def default_control(**overrides) -> AdminControl:
    defaults = dict(
        safe_stop_active=False,
        safe_stop_reason="",
        scheduler_enabled=True,
        global_disable_active=False,
        config_reload_available=True,
        config_reset_available=True,
    )
    defaults.update(overrides)
    return AdminControl(**defaults)


def base_assemble(**overrides):
    defaults = dict(
        control=default_control(),
        total_balance=1000.0,
        available_balance=800.0,
        session_start_balance=1000.0,
        current_balance=1010.0,
        realized_pnl=10.0,
        unrealized_pnl=5.0,
        session_total_pnl=15.0,
        claim_adjusted_balance_effect=0.0,
        blocked_trades=[],
        blocked_rules=[],
        blocked_risk_events=[],
        execution_fill_events=[],
        claim_events=[],
        operational_alerts=[],
    )
    defaults.update(overrides)
    return assemble_admin_report_snapshot(**defaults)


# ---------------------------------------------------------------------------
# TestAdminControl
# ---------------------------------------------------------------------------

class TestAdminControl:
    def test_default_control_state(self):
        ctrl = AdminControl()
        assert ctrl.safe_stop_active is False
        assert ctrl.scheduler_enabled is True
        assert ctrl.global_disable_active is False
        assert ctrl.config_reload_available is True
        assert ctrl.config_reset_available is True

    def test_safe_stop_active(self):
        ctrl = AdminControl(safe_stop_active=True, safe_stop_reason="manual_stop")
        assert ctrl.safe_stop_active is True
        assert ctrl.safe_stop_reason == "manual_stop"

    def test_scheduler_disabled(self):
        ctrl = AdminControl(scheduler_enabled=False)
        assert ctrl.scheduler_enabled is False

    def test_global_disable_active(self):
        ctrl = AdminControl(global_disable_active=True)
        assert ctrl.global_disable_active is True

    def test_config_reload_unavailable(self):
        ctrl = AdminControl(config_reload_available=False)
        assert ctrl.config_reload_available is False

    def test_config_reset_unavailable(self):
        ctrl = AdminControl(config_reset_available=False)
        assert ctrl.config_reset_available is False

    def test_safe_stop_reason_empty_by_default(self):
        ctrl = AdminControl()
        assert ctrl.safe_stop_reason == ""


# ---------------------------------------------------------------------------
# TestAdminReportSnapshot
# ---------------------------------------------------------------------------

class TestAdminReportSnapshot:
    def test_default_snapshot_fields(self):
        snap = AdminReportSnapshot()
        assert snap.safe_stop_active is False
        assert snap.scheduler_enabled is True
        assert snap.blocked_trades == []
        assert snap.operational_alerts == []

    def test_financial_fields_set(self):
        snap = AdminReportSnapshot(
            total_balance=1000.0,
            available_balance=800.0,
            session_start_balance=1000.0,
            current_balance=1010.0,
            realized_pnl=10.0,
            unrealized_pnl=5.0,
            session_total_pnl=15.0,
            claim_adjusted_balance_effect=2.0,
        )
        assert snap.total_balance == 1000.0
        assert snap.realized_pnl == 10.0
        assert snap.claim_adjusted_balance_effect == 2.0

    def test_event_lists_set(self):
        snap = AdminReportSnapshot(
            blocked_trades=["daily_loss_limit_exceeded"],
            blocked_risk_events=["max_concurrent_positions_exceeded"],
            operational_alerts=["safe_stop_triggered"],
        )
        assert "daily_loss_limit_exceeded" in snap.blocked_trades
        assert "max_concurrent_positions_exceeded" in snap.blocked_risk_events
        assert "safe_stop_triggered" in snap.operational_alerts

    def test_realized_unrealized_separate(self):
        snap = AdminReportSnapshot(realized_pnl=10.0, unrealized_pnl=5.0)
        assert snap.realized_pnl != snap.unrealized_pnl

    def test_claim_adjusted_balance_effect_separate(self):
        snap = AdminReportSnapshot(current_balance=1010.0, claim_adjusted_balance_effect=2.0)
        assert snap.current_balance != snap.claim_adjusted_balance_effect


# ---------------------------------------------------------------------------
# TestAssembler
# ---------------------------------------------------------------------------

class TestAssembler:
    def test_assembler_builds_snapshot(self):
        snap = base_assemble()
        assert isinstance(snap, AdminReportSnapshot)

    def test_assembler_copies_control_fields(self):
        ctrl = default_control(safe_stop_active=True, safe_stop_reason="test")
        snap = base_assemble(control=ctrl)
        assert snap.safe_stop_active is True
        assert snap.safe_stop_reason == "test"

    def test_assembler_scheduler_enabled_from_control(self):
        ctrl = default_control(scheduler_enabled=False)
        snap = base_assemble(control=ctrl)
        assert snap.scheduler_enabled is False

    def test_assembler_global_disable_from_control(self):
        ctrl = default_control(global_disable_active=True)
        snap = base_assemble(control=ctrl)
        assert snap.global_disable_active is True

    def test_assembler_config_fields_from_control(self):
        ctrl = default_control(config_reload_available=False, config_reset_available=False)
        snap = base_assemble(control=ctrl)
        assert snap.config_reload_available is False
        assert snap.config_reset_available is False

    def test_assembler_financial_fields_preserved(self):
        snap = base_assemble(
            total_balance=2000.0,
            current_balance=2020.0,
            realized_pnl=20.0,
            claim_adjusted_balance_effect=5.0,
        )
        assert snap.total_balance == 2000.0
        assert snap.current_balance == 2020.0
        assert snap.realized_pnl == 20.0
        assert snap.claim_adjusted_balance_effect == 5.0

    def test_assembler_blocked_trades_preserved(self):
        snap = base_assemble(blocked_trades=["daily_loss_limit_exceeded", "above_max_position_size"])
        assert len(snap.blocked_trades) == 2
        assert "daily_loss_limit_exceeded" in snap.blocked_trades

    def test_assembler_blocked_risk_events_preserved(self):
        snap = base_assemble(blocked_risk_events=["event_limit_exceeded"])
        assert "event_limit_exceeded" in snap.blocked_risk_events

    def test_assembler_execution_fill_events_preserved(self):
        snap = base_assemble(execution_fill_events=["entry_filled", "exit_filled"])
        assert len(snap.execution_fill_events) == 2

    def test_assembler_claim_events_preserved(self):
        snap = base_assemble(claim_events=["claim_completed"])
        assert "claim_completed" in snap.claim_events

    def test_assembler_operational_alerts_preserved(self):
        snap = base_assemble(operational_alerts=["safe_stop_triggered"])
        assert "safe_stop_triggered" in snap.operational_alerts

    def test_assembler_copies_event_lists(self):
        """Assembler must copy lists to prevent external mutation."""
        blocked = ["daily_loss_limit_exceeded"]
        snap = base_assemble(blocked_trades=blocked)
        blocked.clear()
        assert len(snap.blocked_trades) == 1


# ---------------------------------------------------------------------------
# TestAdminLabelMap
# ---------------------------------------------------------------------------

class TestAdminLabelMap:
    def test_operational_control_labels_present(self):
        assert "safe_stop_active" in ADMIN_TURKISH_LABELS
        assert "safe_stop_reason" in ADMIN_TURKISH_LABELS
        assert "scheduler_enabled" in ADMIN_TURKISH_LABELS
        assert "global_disable_active" in ADMIN_TURKISH_LABELS
        assert "config_reload_available" in ADMIN_TURKISH_LABELS
        assert "config_reset_available" in ADMIN_TURKISH_LABELS

    def test_financial_labels_present(self):
        assert "total_balance" in ADMIN_TURKISH_LABELS
        assert "available_balance" in ADMIN_TURKISH_LABELS
        assert "session_start_balance" in ADMIN_TURKISH_LABELS
        assert "current_balance" in ADMIN_TURKISH_LABELS
        assert "realized_pnl" in ADMIN_TURKISH_LABELS
        assert "unrealized_pnl" in ADMIN_TURKISH_LABELS
        assert "session_total_pnl" in ADMIN_TURKISH_LABELS
        assert "claim_adjusted_balance_effect" in ADMIN_TURKISH_LABELS

    def test_event_list_labels_present(self):
        assert "blocked_trades" in ADMIN_TURKISH_LABELS
        assert "blocked_rules" in ADMIN_TURKISH_LABELS
        assert "blocked_risk_events" in ADMIN_TURKISH_LABELS
        assert "execution_fill_events" in ADMIN_TURKISH_LABELS
        assert "claim_events" in ADMIN_TURKISH_LABELS
        assert "operational_alerts" in ADMIN_TURKISH_LABELS

    def test_label_values_are_turkish(self):
        assert ADMIN_TURKISH_LABELS["safe_stop_active"] == "Güvenli Durdurma Aktif"
        assert ADMIN_TURKISH_LABELS["total_balance"] == "Toplam Bakiye"
        assert ADMIN_TURKISH_LABELS["blocked_trades"] == "Bloke Edilen İşlemler"

    def test_all_label_values_nonempty(self):
        for key, value in ADMIN_TURKISH_LABELS.items():
            assert isinstance(value, str) and len(value) > 0, f"Label for '{key}' is empty"
