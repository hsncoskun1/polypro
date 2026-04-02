"""Tests for PersistedPosition model and PositionState."""
from app.domain.position.position_state import PositionState
from app.domain.position.persisted_position import PersistedPosition


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _open_position(
    position_id="pos-001",
    event_key="BTC-USD",
    side="YES",
    trigger_price=0.60,
    order_submitted_price=0.61,
    fill_price=0.62,
    trigger_move_value=0.02,
    fill_move_value=0.0,
    requested_size=10.0,
    filled_size=10.0,
    entry_reason="rule_entry",
    exit_reason="",
    opened_at="2026-04-02T10:00:00Z",
    closed_at=None,
):
    return PersistedPosition(
        position_id=position_id,
        event_key=event_key,
        side=side,
        status=PositionState.OPEN,
        trigger_price=trigger_price,
        order_submitted_price=order_submitted_price,
        fill_price=fill_price,
        trigger_move_value=trigger_move_value,
        fill_move_value=fill_move_value,
        requested_size=requested_size,
        filled_size=filled_size,
        entry_reason=entry_reason,
        exit_reason=exit_reason,
        opened_at=opened_at,
        closed_at=closed_at,
    )


# ---------------------------------------------------------------------------
# TestPositionState
# ---------------------------------------------------------------------------

class TestPositionState:
    def test_open_value(self):
        assert PositionState.OPEN.value == "open"

    def test_closed_value(self):
        assert PositionState.CLOSED.value == "closed"

    def test_from_string_open(self):
        assert PositionState("open") == PositionState.OPEN

    def test_from_string_closed(self):
        assert PositionState("closed") == PositionState.CLOSED


# ---------------------------------------------------------------------------
# TestPersistedPosition
# ---------------------------------------------------------------------------

class TestPersistedPosition:
    def test_open_position_fields(self):
        p = _open_position()
        assert p.position_id == "pos-001"
        assert p.event_key == "BTC-USD"
        assert p.side == "YES"
        assert p.status == PositionState.OPEN
        assert p.trigger_price == 0.60
        assert p.order_submitted_price == 0.61
        assert p.fill_price == 0.62
        assert p.trigger_move_value == 0.02
        assert p.fill_move_value == 0.0
        assert p.requested_size == 10.0
        assert p.filled_size == 10.0
        assert p.entry_reason == "rule_entry"
        assert p.exit_reason == ""
        assert p.opened_at == "2026-04-02T10:00:00Z"
        assert p.closed_at is None

    def test_closed_at_defaults_to_none(self):
        p = _open_position()
        assert p.closed_at is None

    def test_closed_position_has_closed_at(self):
        p = PersistedPosition(
            position_id="pos-002",
            event_key="ETH-USD",
            side="NO",
            status=PositionState.CLOSED,
            trigger_price=0.40,
            order_submitted_price=0.39,
            fill_price=0.38,
            trigger_move_value=0.02,
            fill_move_value=0.05,
            requested_size=5.0,
            filled_size=5.0,
            entry_reason="rule_entry",
            exit_reason="stop_loss",
            opened_at="2026-04-02T10:00:00Z",
            closed_at="2026-04-02T11:00:00Z",
        )
        assert p.status == PositionState.CLOSED
        assert p.exit_reason == "stop_loss"
        assert p.closed_at == "2026-04-02T11:00:00Z"

    def test_trigger_submitted_fill_are_distinct(self):
        """All three price moments are stored independently."""
        p = _open_position(
            trigger_price=0.50,
            order_submitted_price=0.51,
            fill_price=0.52,
        )
        assert p.trigger_price != p.order_submitted_price
        assert p.order_submitted_price != p.fill_price
        assert p.trigger_price != p.fill_price

    def test_requested_and_filled_size_stored(self):
        p = _open_position(requested_size=10.0, filled_size=9.5)
        assert p.requested_size == 10.0
        assert p.filled_size == 9.5
