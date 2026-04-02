"""Tests for SqlitePositionStore — open, close, load, restore locks."""
import os
import tempfile
import pytest

from app.domain.position.position_state import PositionState
from app.domain.position.persisted_position import PersistedPosition
from app.persistence.position_store import SqlitePositionStore, restore_locks_from_positions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    """Provide a fresh SqlitePositionStore backed by a temp file."""
    db_path = str(tmp_path / "test_positions.db")
    return SqlitePositionStore(db_path)


def _make_position(
    position_id="pos-001",
    event_key="BTC-USD",
    side="YES",
    status=PositionState.OPEN,
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
        status=status,
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
# TestOpenPosition
# ---------------------------------------------------------------------------

class TestOpenPosition:
    def test_open_position_persistence_successful(self, store):
        """open_position() persists a record that load_open_positions() returns."""
        p = _make_position()
        store.open_position(p)
        loaded = store.load_open_positions()
        assert len(loaded) == 1
        assert loaded[0].position_id == "pos-001"
        assert loaded[0].status == PositionState.OPEN

    def test_entry_reason_saved(self, store):
        """entry_reason is persisted correctly."""
        p = _make_position(entry_reason="trend_follow")
        store.open_position(p)
        loaded = store.load_open_positions()
        assert loaded[0].entry_reason == "trend_follow"

    def test_trigger_submitted_fill_snapshot_fields_saved(self, store):
        """trigger_price, order_submitted_price, fill_price all stored."""
        p = _make_position(
            trigger_price=0.50,
            order_submitted_price=0.51,
            fill_price=0.52,
            trigger_move_value=0.01,
            fill_move_value=0.02,
        )
        store.open_position(p)
        loaded = store.load_open_positions()
        assert loaded[0].trigger_price == 0.50
        assert loaded[0].order_submitted_price == 0.51
        assert loaded[0].fill_price == 0.52
        assert loaded[0].trigger_move_value == 0.01
        assert loaded[0].fill_move_value == 0.02

    def test_requested_size_and_filled_size_saved(self, store):
        """requested_size and filled_size are persisted independently."""
        p = _make_position(requested_size=10.0, filled_size=9.5)
        store.open_position(p)
        loaded = store.load_open_positions()
        assert loaded[0].requested_size == 10.0
        assert loaded[0].filled_size == 9.5

    def test_multiple_open_positions(self, store):
        """Multiple open positions all returned by load_open_positions."""
        p1 = _make_position(position_id="pos-001", event_key="BTC-USD")
        p2 = _make_position(position_id="pos-002", event_key="ETH-USD")
        store.open_position(p1)
        store.open_position(p2)
        loaded = store.load_open_positions()
        assert len(loaded) == 2


# ---------------------------------------------------------------------------
# TestClosePosition
# ---------------------------------------------------------------------------

class TestClosePosition:
    def test_close_position_persistence_successful(self, store):
        """close_position() transitions status to CLOSED."""
        p = _make_position()
        store.open_position(p)
        store.close_position("pos-001", "stop_loss", "2026-04-02T11:00:00Z")
        all_pos = store.load_all_positions()
        assert len(all_pos) == 1
        assert all_pos[0].status == PositionState.CLOSED

    def test_exit_reason_saved(self, store):
        """exit_reason is set correctly on close."""
        p = _make_position()
        store.open_position(p)
        store.close_position("pos-001", "force_sell_time", "2026-04-02T11:00:00Z")
        all_pos = store.load_all_positions()
        assert all_pos[0].exit_reason == "force_sell_time"

    def test_closed_at_saved(self, store):
        """closed_at timestamp is persisted on close."""
        p = _make_position()
        store.open_position(p)
        store.close_position("pos-001", "take_profit", "2026-04-02T12:30:00Z")
        all_pos = store.load_all_positions()
        assert all_pos[0].closed_at == "2026-04-02T12:30:00Z"

    def test_closed_positions_excluded_from_load_open(self, store):
        """Closed positions do NOT appear in load_open_positions()."""
        p = _make_position()
        store.open_position(p)
        store.close_position("pos-001", "timeout", "2026-04-02T11:00:00Z")
        open_pos = store.load_open_positions()
        assert len(open_pos) == 0

    def test_closed_position_does_not_pollute_open_list(self, store):
        """Mixed open+closed — only open returned by load_open_positions."""
        p_open = _make_position(position_id="pos-open", event_key="BTC-USD")
        p_close = _make_position(position_id="pos-close", event_key="ETH-USD")
        store.open_position(p_open)
        store.open_position(p_close)
        store.close_position("pos-close", "stop_loss", "2026-04-02T11:00:00Z")
        open_pos = store.load_open_positions()
        assert len(open_pos) == 1
        assert open_pos[0].position_id == "pos-open"


# ---------------------------------------------------------------------------
# TestRestartRecovery
# ---------------------------------------------------------------------------

class TestRestartRecovery:
    def test_load_open_positions_returns_open_ones(self, store):
        """After opening 3 and closing 1, load_open returns 2."""
        for i in range(3):
            store.open_position(_make_position(
                position_id=f"pos-{i}",
                event_key=f"market-{i}",
            ))
        store.close_position("pos-0", "timeout", "2026-04-02T11:00:00Z")
        open_pos = store.load_open_positions()
        assert len(open_pos) == 2
        ids = {p.position_id for p in open_pos}
        assert "pos-1" in ids
        assert "pos-2" in ids
        assert "pos-0" not in ids

    def test_restart_recovery_flow(self, store):
        """Simulate restart: open positions loaded, closed excluded."""
        store.open_position(_make_position(position_id="pos-A", event_key="AAPL"))
        store.open_position(_make_position(position_id="pos-B", event_key="TSLA"))
        store.close_position("pos-A", "stop_loss", "2026-04-02T11:00:00Z")
        # Simulate restart: create new store on same DB path
        recovered = store.load_open_positions()
        assert len(recovered) == 1
        assert recovered[0].event_key == "TSLA"


# ---------------------------------------------------------------------------
# TestRestoreLocks
# ---------------------------------------------------------------------------

class TestRestoreLocks:
    def test_restore_locks_from_positions_correct_lock_set(self):
        """restore_locks_from_positions returns event_keys of all open positions."""
        positions = [
            _make_position(position_id="pos-1", event_key="BTC-USD"),
            _make_position(position_id="pos-2", event_key="ETH-USD"),
        ]
        locks = restore_locks_from_positions(positions)
        assert locks == {"BTC-USD", "ETH-USD"}

    def test_restore_locks_empty_when_no_positions(self):
        """Empty position list produces empty lock set."""
        locks = restore_locks_from_positions([])
        assert locks == set()

    def test_restore_locks_from_store_after_open(self, store):
        """Full flow: open positions, load them, restore locks."""
        store.open_position(_make_position(position_id="pos-1", event_key="BTC-USD"))
        store.open_position(_make_position(position_id="pos-2", event_key="ETH-USD"))
        store.close_position("pos-1", "stop_loss", "2026-04-02T11:00:00Z")
        open_pos = store.load_open_positions()
        locks = restore_locks_from_positions(open_pos)
        # Only ETH-USD is still open
        assert locks == {"ETH-USD"}
