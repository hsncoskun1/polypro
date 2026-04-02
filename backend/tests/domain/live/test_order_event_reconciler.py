"""Tests for live order event stream + state reconciliation foundation — v0.7.6."""
from app.domain.live.live_order_event_type import LiveOrderEventType
from app.domain.live.live_order_event import LiveOrderEvent
from app.domain.live.live_order_state import LiveOrderState
from app.domain.live.reconciliation_status import ReconciliationStatus
from app.domain.live.live_order_reconciliation_result import LiveOrderReconciliationResult
from app.domain.live.order_event_reconciler import reconcile_order_events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_event(event_type: LiveOrderEventType, **kwargs) -> LiveOrderEvent:
    defaults = dict(order_id="ord_001")
    defaults.update(kwargs)
    return LiveOrderEvent(event_type=event_type, **defaults)


# ---------------------------------------------------------------------------
# TestLiveOrderEventType
# ---------------------------------------------------------------------------

class TestLiveOrderEventType:
    def test_order_submitted(self):
        assert LiveOrderEventType.ORDER_SUBMITTED == "order_submitted"

    def test_order_accepted(self):
        assert LiveOrderEventType.ORDER_ACCEPTED == "order_accepted"

    def test_order_partially_filled(self):
        assert LiveOrderEventType.ORDER_PARTIALLY_FILLED == "order_partially_filled"

    def test_order_filled(self):
        assert LiveOrderEventType.ORDER_FILLED == "order_filled"

    def test_order_cancel_requested(self):
        assert LiveOrderEventType.ORDER_CANCEL_REQUESTED == "order_cancel_requested"

    def test_order_cancelled(self):
        assert LiveOrderEventType.ORDER_CANCELLED == "order_cancelled"

    def test_order_replace_requested(self):
        assert LiveOrderEventType.ORDER_REPLACE_REQUESTED == "order_replace_requested"

    def test_order_replaced(self):
        assert LiveOrderEventType.ORDER_REPLACED == "order_replaced"

    def test_order_rejected(self):
        assert LiveOrderEventType.ORDER_REJECTED == "order_rejected"

    def test_order_expired(self):
        assert LiveOrderEventType.ORDER_EXPIRED == "order_expired"

    def test_order_failed(self):
        assert LiveOrderEventType.ORDER_FAILED == "order_failed"

    def test_is_str_enum(self):
        assert isinstance(LiveOrderEventType.ORDER_FILLED, str)


# ---------------------------------------------------------------------------
# TestLiveOrderEvent
# ---------------------------------------------------------------------------

class TestLiveOrderEvent:
    def test_required_fields(self):
        e = LiveOrderEvent(order_id="ord_001", event_type=LiveOrderEventType.ORDER_SUBMITTED)
        assert e.order_id == "ord_001"
        assert e.event_type == LiveOrderEventType.ORDER_SUBMITTED

    def test_defaults(self):
        e = LiveOrderEvent(order_id="ord_001", event_type=LiveOrderEventType.ORDER_SUBMITTED)
        assert e.client_order_id == ""
        assert e.event_timestamp == ""
        assert e.side == ""
        assert e.requested_size == 0.0
        assert e.filled_size == 0.0
        assert e.remaining_size == 0.0
        assert e.limit_price == 0.0
        assert e.reject_reason == ""
        assert e.is_terminal is False

    def test_full_fields(self):
        e = LiveOrderEvent(
            order_id="ord_002",
            event_type=LiveOrderEventType.ORDER_PARTIALLY_FILLED,
            client_order_id="client_001",
            event_timestamp="2026-04-02T10:00:00",
            side="buy",
            requested_size=100.0,
            filled_size=40.0,
            remaining_size=60.0,
            limit_price=0.75,
        )
        assert e.client_order_id == "client_001"
        assert e.side == "buy"
        assert e.filled_size == 40.0
        assert e.remaining_size == 60.0


# ---------------------------------------------------------------------------
# TestLiveOrderState
# ---------------------------------------------------------------------------

class TestLiveOrderState:
    def test_required_fields(self):
        s = LiveOrderState(order_id="ord_001")
        assert s.order_id == "ord_001"

    def test_defaults(self):
        s = LiveOrderState(order_id="ord_001")
        assert s.client_order_id == ""
        assert s.side == ""
        assert s.requested_size == 0.0
        assert s.filled_size == 0.0
        assert s.remaining_size == 0.0
        assert s.limit_price == 0.0
        assert s.current_event_type is None
        assert s.is_cancelled is False
        assert s.is_filled is False
        assert s.is_terminal is False
        assert s.last_event_timestamp == ""
        assert s.event_count == 0


# ---------------------------------------------------------------------------
# TestReconciliationStatus
# ---------------------------------------------------------------------------

class TestReconciliationStatus:
    def test_reconciled(self):
        assert ReconciliationStatus.RECONCILED == "reconciled"

    def test_no_events(self):
        assert ReconciliationStatus.NO_EVENTS == "no_events"

    def test_conflicting_events(self):
        assert ReconciliationStatus.CONFLICTING_EVENTS == "conflicting_events"

    def test_terminal_state(self):
        assert ReconciliationStatus.TERMINAL_STATE == "terminal_state"

    def test_is_str_enum(self):
        assert isinstance(ReconciliationStatus.RECONCILED, str)


# ---------------------------------------------------------------------------
# TestLiveOrderReconciliationResult
# ---------------------------------------------------------------------------

class TestLiveOrderReconciliationResult:
    def test_required_fields(self):
        r = LiveOrderReconciliationResult(
            order_id="ord_001",
            reconciliation_status=ReconciliationStatus.RECONCILED,
        )
        assert r.order_id == "ord_001"
        assert r.reconciliation_status == ReconciliationStatus.RECONCILED

    def test_defaults(self):
        r = LiveOrderReconciliationResult(
            order_id="ord_001",
            reconciliation_status=ReconciliationStatus.NO_EVENTS,
        )
        assert r.final_state is None
        assert r.events_processed == 0
        assert r.is_terminal is False
        assert r.reconciled_at == ""


# ---------------------------------------------------------------------------
# TestReconcileOrderEvents — No Events
# ---------------------------------------------------------------------------

class TestReconcileNoEvents:
    def test_no_events_returns_no_events_status(self):
        result = reconcile_order_events("ord_001", [])
        assert result.reconciliation_status == ReconciliationStatus.NO_EVENTS

    def test_no_events_final_state_is_none(self):
        result = reconcile_order_events("ord_001", [])
        assert result.final_state is None

    def test_no_events_processed_zero(self):
        result = reconcile_order_events("ord_001", [])
        assert result.events_processed == 0

    def test_no_events_not_terminal(self):
        result = reconcile_order_events("ord_001", [])
        assert result.is_terminal is False

    def test_no_events_order_id_preserved(self):
        result = reconcile_order_events("ord_999", [])
        assert result.order_id == "ord_999"


# ---------------------------------------------------------------------------
# TestReconcileOrderEvents — Single Events
# ---------------------------------------------------------------------------

class TestReconcileSingleEvent:
    def test_submitted_returns_reconciled(self):
        events = [make_event(LiveOrderEventType.ORDER_SUBMITTED)]
        result = reconcile_order_events("ord_001", events)
        assert result.reconciliation_status == ReconciliationStatus.RECONCILED

    def test_submitted_event_count_one(self):
        events = [make_event(LiveOrderEventType.ORDER_SUBMITTED)]
        result = reconcile_order_events("ord_001", events)
        assert result.events_processed == 1
        assert result.final_state.event_count == 1

    def test_accepted_not_terminal(self):
        events = [make_event(LiveOrderEventType.ORDER_ACCEPTED)]
        result = reconcile_order_events("ord_001", events)
        assert result.is_terminal is False

    def test_filled_is_terminal(self):
        events = [make_event(LiveOrderEventType.ORDER_FILLED, requested_size=10.0)]
        result = reconcile_order_events("ord_001", events)
        assert result.is_terminal is True
        assert result.reconciliation_status == ReconciliationStatus.TERMINAL_STATE

    def test_cancelled_is_terminal(self):
        events = [make_event(LiveOrderEventType.ORDER_CANCELLED)]
        result = reconcile_order_events("ord_001", events)
        assert result.is_terminal is True

    def test_rejected_is_terminal(self):
        events = [make_event(LiveOrderEventType.ORDER_REJECTED)]
        result = reconcile_order_events("ord_001", events)
        assert result.is_terminal is True

    def test_expired_is_terminal(self):
        events = [make_event(LiveOrderEventType.ORDER_EXPIRED)]
        result = reconcile_order_events("ord_001", events)
        assert result.is_terminal is True

    def test_failed_is_terminal(self):
        events = [make_event(LiveOrderEventType.ORDER_FAILED)]
        result = reconcile_order_events("ord_001", events)
        assert result.is_terminal is True


# ---------------------------------------------------------------------------
# TestReconcileOrderEvents — State Transitions
# ---------------------------------------------------------------------------

class TestReconcileStateTransitions:
    def test_submit_then_accept(self):
        events = [
            make_event(LiveOrderEventType.ORDER_SUBMITTED, side="buy", requested_size=10.0),
            make_event(LiveOrderEventType.ORDER_ACCEPTED),
        ]
        result = reconcile_order_events("ord_001", events)
        assert result.events_processed == 2
        assert result.final_state.current_event_type == LiveOrderEventType.ORDER_ACCEPTED
        assert result.is_terminal is False

    def test_partial_fill_not_terminal(self):
        events = [
            make_event(LiveOrderEventType.ORDER_SUBMITTED, requested_size=100.0),
            make_event(LiveOrderEventType.ORDER_PARTIALLY_FILLED, filled_size=40.0, remaining_size=60.0),
        ]
        result = reconcile_order_events("ord_001", events)
        assert result.final_state.filled_size == 40.0
        assert result.final_state.remaining_size == 60.0
        assert result.is_terminal is False

    def test_full_fill_is_terminal(self):
        events = [
            make_event(LiveOrderEventType.ORDER_SUBMITTED, requested_size=10.0),
            make_event(LiveOrderEventType.ORDER_FILLED, requested_size=10.0, filled_size=10.0),
        ]
        result = reconcile_order_events("ord_001", events)
        assert result.final_state.is_filled is True
        assert result.final_state.is_terminal is True
        assert result.final_state.remaining_size == 0.0

    def test_partial_then_full_fill(self):
        events = [
            make_event(LiveOrderEventType.ORDER_SUBMITTED, requested_size=10.0),
            make_event(LiveOrderEventType.ORDER_PARTIALLY_FILLED, filled_size=5.0, remaining_size=5.0),
            make_event(LiveOrderEventType.ORDER_FILLED, filled_size=10.0),
        ]
        result = reconcile_order_events("ord_001", events)
        assert result.final_state.is_filled is True
        assert result.is_terminal is True
        assert result.events_processed == 3

    def test_cancel_request_then_cancelled(self):
        events = [
            make_event(LiveOrderEventType.ORDER_SUBMITTED, requested_size=10.0),
            make_event(LiveOrderEventType.ORDER_CANCEL_REQUESTED),
            make_event(LiveOrderEventType.ORDER_CANCELLED),
        ]
        result = reconcile_order_events("ord_001", events)
        assert result.final_state.is_cancelled is True
        assert result.final_state.is_terminal is True

    def test_replace_request_then_replaced(self):
        events = [
            make_event(LiveOrderEventType.ORDER_SUBMITTED, requested_size=10.0, limit_price=0.75),
            make_event(LiveOrderEventType.ORDER_REPLACE_REQUESTED),
            make_event(LiveOrderEventType.ORDER_REPLACED, limit_price=0.80, requested_size=15.0),
        ]
        result = reconcile_order_events("ord_001", events)
        assert result.final_state.limit_price == 0.80
        assert result.final_state.requested_size == 15.0
        assert result.is_terminal is False

    def test_order_id_preserved_in_state(self):
        events = [make_event(LiveOrderEventType.ORDER_SUBMITTED, order_id="ord_777")]
        result = reconcile_order_events("ord_777", events)
        assert result.order_id == "ord_777"
        assert result.final_state.order_id == "ord_777"

    def test_side_carried(self):
        events = [make_event(LiveOrderEventType.ORDER_SUBMITTED, side="sell")]
        result = reconcile_order_events("ord_001", events)
        assert result.final_state.side == "sell"

    def test_timestamp_updated_by_latest_event(self):
        events = [
            make_event(LiveOrderEventType.ORDER_SUBMITTED, event_timestamp="2026-04-02T10:00:00"),
            make_event(LiveOrderEventType.ORDER_ACCEPTED, event_timestamp="2026-04-02T10:00:01"),
        ]
        result = reconcile_order_events("ord_001", events)
        assert result.final_state.last_event_timestamp == "2026-04-02T10:00:01"

    def test_event_count_tracks_all_events(self):
        events = [
            make_event(LiveOrderEventType.ORDER_SUBMITTED),
            make_event(LiveOrderEventType.ORDER_ACCEPTED),
            make_event(LiveOrderEventType.ORDER_PARTIALLY_FILLED, filled_size=5.0),
            make_event(LiveOrderEventType.ORDER_FILLED),
        ]
        result = reconcile_order_events("ord_001", events)
        assert result.final_state.event_count == 4

    def test_submission_and_cancel_replace_seams_not_collapsed(self):
        """v0.7.3/v0.7.5 seams must remain separate — reconciler does not duplicate them."""
        cancel_events = [make_event(LiveOrderEventType.ORDER_CANCELLED)]
        replace_events = [make_event(LiveOrderEventType.ORDER_REPLACED)]
        cancel_result = reconcile_order_events("ord_c", cancel_events)
        replace_result = reconcile_order_events("ord_r", replace_events)
        assert cancel_result.final_state.is_cancelled is True
        assert replace_result.final_state.is_cancelled is False
