"""Tests for EventType and EventRecord."""
from app.domain.event_log.event_type import EventType
from app.domain.event_log.event_record import EventRecord


# ---------------------------------------------------------------------------
# TestEventType
# ---------------------------------------------------------------------------

class TestEventType:
    def test_all_expected_event_types_present(self):
        """All required event types from v0.5.4 spec are present."""
        expected = {
            "decision_passed",
            "entry_order_submitted",
            "entry_filled",
            "position_opened",
            "exit_triggered",
            "exit_order_submitted",
            "exit_filled",
            "position_closed",
            "claim_available",
            "claim_completed",
            "balance_updated",
        }
        actual = {e.value for e in EventType}
        assert expected == actual

    def test_from_string(self):
        assert EventType("entry_filled") == EventType.ENTRY_FILLED

    def test_claim_events_are_seams(self):
        """Claim events exist as seam types."""
        assert EventType.CLAIM_AVAILABLE.value == "claim_available"
        assert EventType.CLAIM_COMPLETED.value == "claim_completed"

    def test_two_phase_entry_model(self):
        """Entry has submitted + filled as separate events."""
        assert EventType.ENTRY_ORDER_SUBMITTED != EventType.ENTRY_FILLED

    def test_two_phase_exit_model(self):
        """Exit has submitted + filled as separate events."""
        assert EventType.EXIT_ORDER_SUBMITTED != EventType.EXIT_FILLED


# ---------------------------------------------------------------------------
# TestEventRecord
# ---------------------------------------------------------------------------

class TestEventRecord:
    def test_event_record_fields_set_correctly(self):
        record = EventRecord(
            event_type=EventType.ENTRY_FILLED,
            event_key="BTC-USD",
            timestamp="2026-04-02T10:00:00Z",
            payload={"fill_price": 0.50, "filled_size": 10.0},
        )
        assert record.event_type == EventType.ENTRY_FILLED
        assert record.event_key == "BTC-USD"
        assert record.timestamp == "2026-04-02T10:00:00Z"
        assert record.payload["fill_price"] == 0.50

    def test_payload_defaults_to_empty_dict(self):
        record = EventRecord(
            event_type=EventType.DECISION_PASSED,
            event_key="ETH-USD",
            timestamp="2026-04-02T10:00:00Z",
        )
        assert record.payload == {}

    def test_position_opened_event(self):
        record = EventRecord(
            event_type=EventType.POSITION_OPENED,
            event_key="BTC-USD",
            timestamp="2026-04-02T10:00:00Z",
            payload={"entry_fill_price": 0.60, "side": "YES"},
        )
        assert record.event_type == EventType.POSITION_OPENED

    def test_position_closed_event(self):
        record = EventRecord(
            event_type=EventType.POSITION_CLOSED,
            event_key="BTC-USD",
            timestamp="2026-04-02T11:00:00Z",
            payload={"exit_reason": "stop_loss", "realized_pnl": -1.5},
        )
        assert record.event_type == EventType.POSITION_CLOSED
        assert record.payload["exit_reason"] == "stop_loss"

    def test_balance_updated_seam_event(self):
        record = EventRecord(
            event_type=EventType.BALANCE_UPDATED,
            event_key="BTC-USD",
            timestamp="2026-04-02T11:00:00Z",
            payload={"current_balance": 1002.0},
        )
        assert record.event_type == EventType.BALANCE_UPDATED
