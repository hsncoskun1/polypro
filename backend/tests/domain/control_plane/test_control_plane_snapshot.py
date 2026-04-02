"""Tests for simulation control plane read model — v0.6.1."""
from app.domain.control_plane.position_view import PositionView
from app.domain.control_plane.control_plane_snapshot import ControlPlaneSnapshot
from app.domain.control_plane.control_plane_assembler import assemble_control_plane_snapshot
from app.domain.control_plane.label_map import TURKISH_LABELS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def open_position_view(**overrides) -> PositionView:
    defaults = dict(
        position_id="pos-001",
        event_key="BTC-USD",
        side="YES",
        status="open",
        trigger_price=0.50,
        entry_fill_price=0.52,
        current_price=0.60,
        exit_fill_price=0.0,
        trigger_move_value=0.0,
        fill_move_value=0.02,
        current_move_value=0.08,
        realized_pnl=0.0,
        unrealized_pnl=8.0,
        entry_reason="strategy_pass",
        exit_reason="",
        opened_at="2026-04-02T10:00:00Z",
        closed_at=None,
    )
    defaults.update(overrides)
    return PositionView(**defaults)


def closed_position_view(**overrides) -> PositionView:
    defaults = dict(
        position_id="pos-002",
        event_key="ETH-USD",
        side="NO",
        status="closed",
        trigger_price=0.40,
        entry_fill_price=0.42,
        current_price=0.30,
        exit_fill_price=0.28,
        trigger_move_value=0.0,
        fill_move_value=-0.02,
        current_move_value=-0.14,
        realized_pnl=-14.0,
        unrealized_pnl=0.0,
        entry_reason="strategy_pass",
        exit_reason="stop_loss",
        opened_at="2026-04-02T09:00:00Z",
        closed_at="2026-04-02T11:00:00Z",
    )
    defaults.update(overrides)
    return PositionView(**defaults)


def base_snapshot(**overrides):
    defaults = dict(
        open_positions=[],
        closed_positions=[],
        session_realized_pnl=0.0,
        session_unrealized_pnl=0.0,
        session_total_pnl=0.0,
        total_balance=1000.0,
        available_balance=800.0,
        current_balance=1000.0,
        session_start_balance=1000.0,
        claim_status="claim_available",
        claim_available=True,
        claimed_amount=0.0,
        settlement_completed_at=None,
    )
    defaults.update(overrides)
    return assemble_control_plane_snapshot(**defaults)


# ---------------------------------------------------------------------------
# TestPositionView
# ---------------------------------------------------------------------------

class TestPositionView:
    def test_open_position_fields(self):
        pos = open_position_view()
        assert pos.position_id == "pos-001"
        assert pos.status == "open"
        assert pos.exit_fill_price == 0.0
        assert pos.closed_at is None
        assert pos.exit_reason == ""

    def test_closed_position_fields(self):
        pos = closed_position_view()
        assert pos.status == "closed"
        assert pos.exit_fill_price == 0.28
        assert pos.closed_at == "2026-04-02T11:00:00Z"
        assert pos.exit_reason == "stop_loss"

    def test_trigger_fill_current_are_distinct(self):
        pos = open_position_view(
            trigger_price=0.50,
            entry_fill_price=0.52,
            current_price=0.60,
        )
        assert pos.trigger_price != pos.entry_fill_price
        assert pos.entry_fill_price != pos.current_price
        assert pos.trigger_price != pos.current_price

    def test_trigger_fill_move_values_are_distinct(self):
        pos = open_position_view(
            trigger_move_value=0.0,
            fill_move_value=0.02,
            current_move_value=0.08,
        )
        assert pos.trigger_move_value != pos.current_move_value

    def test_realized_pnl_zero_for_open_position(self):
        pos = open_position_view()
        assert pos.realized_pnl == 0.0

    def test_unrealized_pnl_zero_for_closed_position(self):
        pos = closed_position_view()
        assert pos.unrealized_pnl == 0.0

    def test_side_field_preserved(self):
        yes_pos = open_position_view(side="YES")
        no_pos = closed_position_view(side="NO")
        assert yes_pos.side == "YES"
        assert no_pos.side == "NO"


# ---------------------------------------------------------------------------
# TestControlPlaneSnapshot
# ---------------------------------------------------------------------------

class TestControlPlaneSnapshot:
    def test_empty_snapshot_defaults(self):
        snap = ControlPlaneSnapshot()
        assert snap.open_positions == []
        assert snap.closed_positions == []
        assert snap.claim_available is False

    def test_open_closed_positions_separate(self):
        open_pos = open_position_view()
        closed_pos = closed_position_view()
        snap = ControlPlaneSnapshot(
            open_positions=[open_pos],
            closed_positions=[closed_pos],
        )
        assert len(snap.open_positions) == 1
        assert len(snap.closed_positions) == 1
        assert snap.open_positions[0].status == "open"
        assert snap.closed_positions[0].status == "closed"

    def test_session_pnl_fields_all_present(self):
        snap = ControlPlaneSnapshot(
            session_realized_pnl=10.0,
            session_unrealized_pnl=5.0,
            session_total_pnl=15.0,
        )
        assert snap.session_realized_pnl == 10.0
        assert snap.session_unrealized_pnl == 5.0
        assert snap.session_total_pnl == 15.0

    def test_session_pnl_fields_are_independent(self):
        snap = ControlPlaneSnapshot(
            session_realized_pnl=10.0,
            session_unrealized_pnl=5.0,
            session_total_pnl=15.0,
        )
        assert snap.session_realized_pnl != snap.session_unrealized_pnl

    def test_balance_fields_all_present(self):
        snap = ControlPlaneSnapshot(
            total_balance=1000.0,
            available_balance=800.0,
            current_balance=1010.0,
            session_start_balance=1000.0,
        )
        assert snap.total_balance == 1000.0
        assert snap.available_balance == 800.0
        assert snap.current_balance == 1010.0
        assert snap.session_start_balance == 1000.0

    def test_claim_section_fields(self):
        snap = ControlPlaneSnapshot(
            claim_status="claim_completed",
            claim_available=False,
            claimed_amount=100.0,
            settlement_completed_at="2026-04-02T12:00:00Z",
        )
        assert snap.claim_status == "claim_completed"
        assert snap.claim_available is False
        assert snap.claimed_amount == 100.0
        assert snap.settlement_completed_at == "2026-04-02T12:00:00Z"

    def test_claim_available_separately_from_status(self):
        snap = ControlPlaneSnapshot(claim_status="claim_available", claim_available=True)
        assert snap.claim_status == "claim_available"
        assert snap.claim_available is True


# ---------------------------------------------------------------------------
# TestAssembler
# ---------------------------------------------------------------------------

class TestAssembler:
    def test_assembler_builds_correct_snapshot(self):
        snap = base_snapshot()
        assert isinstance(snap, ControlPlaneSnapshot)
        assert snap.total_balance == 1000.0
        assert snap.claim_available is True

    def test_assembler_preserves_open_positions(self):
        open_pos = open_position_view()
        snap = base_snapshot(open_positions=[open_pos])
        assert len(snap.open_positions) == 1
        assert snap.open_positions[0].position_id == "pos-001"

    def test_assembler_preserves_closed_positions(self):
        closed_pos = closed_position_view()
        snap = base_snapshot(closed_positions=[closed_pos])
        assert len(snap.closed_positions) == 1
        assert snap.closed_positions[0].position_id == "pos-002"

    def test_assembler_open_closed_not_mixed(self):
        open_pos = open_position_view()
        closed_pos = closed_position_view()
        snap = base_snapshot(open_positions=[open_pos], closed_positions=[closed_pos])
        assert snap.open_positions[0].status == "open"
        assert snap.closed_positions[0].status == "closed"

    def test_assembler_session_pnl_preserved(self):
        snap = base_snapshot(
            session_realized_pnl=20.0,
            session_unrealized_pnl=8.0,
            session_total_pnl=28.0,
        )
        assert snap.session_realized_pnl == 20.0
        assert snap.session_unrealized_pnl == 8.0
        assert snap.session_total_pnl == 28.0

    def test_assembler_claim_settlement_preserved(self):
        snap = base_snapshot(
            claim_status="claim_completed",
            claim_available=False,
            claimed_amount=75.0,
            settlement_completed_at="2026-04-02T12:00:00Z",
        )
        assert snap.claim_status == "claim_completed"
        assert snap.claimed_amount == 75.0
        assert snap.settlement_completed_at == "2026-04-02T12:00:00Z"

    def test_assembler_makes_copy_of_position_lists(self):
        """Assembler should not share mutable list references."""
        open_list = [open_position_view()]
        snap = assemble_control_plane_snapshot(
            open_positions=open_list,
            closed_positions=[],
            session_realized_pnl=0.0,
            session_unrealized_pnl=0.0,
            session_total_pnl=0.0,
            total_balance=1000.0,
            available_balance=800.0,
            current_balance=1000.0,
            session_start_balance=1000.0,
            claim_status="",
            claim_available=False,
            claimed_amount=0.0,
            settlement_completed_at=None,
        )
        open_list.clear()
        assert len(snap.open_positions) == 1  # snapshot not affected


# ---------------------------------------------------------------------------
# TestLabelMap
# ---------------------------------------------------------------------------

class TestLabelMap:
    def test_required_price_labels_present(self):
        assert "trigger_price" in TURKISH_LABELS
        assert "entry_fill_price" in TURKISH_LABELS
        assert "current_price" in TURKISH_LABELS
        assert "exit_fill_price" in TURKISH_LABELS

    def test_required_move_labels_present(self):
        assert "trigger_move_value" in TURKISH_LABELS
        assert "fill_move_value" in TURKISH_LABELS
        assert "current_move_value" in TURKISH_LABELS

    def test_required_pnl_labels_present(self):
        assert "realized_pnl" in TURKISH_LABELS
        assert "unrealized_pnl" in TURKISH_LABELS
        assert "session_realized_pnl" in TURKISH_LABELS
        assert "session_unrealized_pnl" in TURKISH_LABELS
        assert "session_total_pnl" in TURKISH_LABELS

    def test_required_balance_labels_present(self):
        assert "total_balance" in TURKISH_LABELS
        assert "available_balance" in TURKISH_LABELS
        assert "current_balance" in TURKISH_LABELS
        assert "session_start_balance" in TURKISH_LABELS

    def test_required_claim_labels_present(self):
        assert "claim_status" in TURKISH_LABELS
        assert "claim_available" in TURKISH_LABELS
        assert "claimed_amount" in TURKISH_LABELS
        assert "settlement_completed_at" in TURKISH_LABELS

    def test_position_list_labels_present(self):
        assert "open_positions" in TURKISH_LABELS
        assert "closed_positions" in TURKISH_LABELS

    def test_labels_are_turkish_strings(self):
        assert TURKISH_LABELS["open_positions"] == "Açık Pozisyonlar"
        assert TURKISH_LABELS["closed_positions"] == "Kapalı Pozisyonlar"
        assert TURKISH_LABELS["realized_pnl"] == "Gerçekleşen K/Z"
        assert TURKISH_LABELS["total_balance"] == "Toplam Bakiye"

    def test_all_label_values_are_nonempty_strings(self):
        for key, value in TURKISH_LABELS.items():
            assert isinstance(value, str) and len(value) > 0, f"Label for '{key}' is empty"
