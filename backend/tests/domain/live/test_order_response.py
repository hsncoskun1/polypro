"""Tests for live order response classification + fill confirmation — v0.7.4."""
from app.domain.live.order_response_status import OrderResponseStatus
from app.domain.live.fill_confirmation_status import FillConfirmationStatus
from app.domain.live.live_order_response import LiveOrderResponse
from app.domain.live.fill_confirmation import FillConfirmation
from app.domain.live.order_response_classifier import (
    classify_order_response,
    build_fill_confirmation,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def base_response(**overrides) -> dict:
    """Base kwargs for classify_order_response — all-clear submitted state."""
    defaults = dict(
        order_id="ord_001",
        requested_size=10.0,
        accepted_size=0.0,
        filled_size=0.0,
        exchange_acknowledged=False,
        rejected=False,
        retryable=False,
        terminal_failure=False,
        reject_reason="",
        response_received_at="",
        fill_confirmed_at="",
    )
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------------
# TestOrderResponseStatus
# ---------------------------------------------------------------------------

class TestOrderResponseStatus:
    def test_submitted_value(self):
        assert OrderResponseStatus.SUBMITTED == "submitted"

    def test_accepted_value(self):
        assert OrderResponseStatus.ACCEPTED == "accepted"

    def test_partially_filled_value(self):
        assert OrderResponseStatus.PARTIALLY_FILLED == "partially_filled"

    def test_filled_value(self):
        assert OrderResponseStatus.FILLED == "filled"

    def test_rejected_value(self):
        assert OrderResponseStatus.REJECTED == "rejected"

    def test_retryable_failure_value(self):
        assert OrderResponseStatus.RETRYABLE_FAILURE == "retryable_failure"

    def test_terminal_failure_value(self):
        assert OrderResponseStatus.TERMINAL_FAILURE == "terminal_failure"

    def test_is_str_enum(self):
        assert isinstance(OrderResponseStatus.FILLED, str)


# ---------------------------------------------------------------------------
# TestFillConfirmationStatus
# ---------------------------------------------------------------------------

class TestFillConfirmationStatus:
    def test_not_confirmed_value(self):
        assert FillConfirmationStatus.NOT_CONFIRMED == "not_confirmed"

    def test_partially_confirmed_value(self):
        assert FillConfirmationStatus.PARTIALLY_CONFIRMED == "partially_confirmed"

    def test_fully_confirmed_value(self):
        assert FillConfirmationStatus.FULLY_CONFIRMED == "fully_confirmed"

    def test_confirmation_failed_value(self):
        assert FillConfirmationStatus.CONFIRMATION_FAILED == "confirmation_failed"

    def test_is_str_enum(self):
        assert isinstance(FillConfirmationStatus.FULLY_CONFIRMED, str)


# ---------------------------------------------------------------------------
# TestLiveOrderResponse
# ---------------------------------------------------------------------------

class TestLiveOrderResponse:
    def test_required_fields(self):
        resp = LiveOrderResponse(
            order_id="ord_001",
            order_response_status=OrderResponseStatus.SUBMITTED,
            requested_size=10.0,
        )
        assert resp.order_id == "ord_001"
        assert resp.order_response_status == OrderResponseStatus.SUBMITTED
        assert resp.requested_size == 10.0

    def test_defaults(self):
        resp = LiveOrderResponse(
            order_id="ord_001",
            order_response_status=OrderResponseStatus.SUBMITTED,
            requested_size=10.0,
        )
        assert resp.accepted_size == 0.0
        assert resp.filled_size == 0.0
        assert resp.remaining_size == 0.0
        assert resp.retryable is False
        assert resp.terminal_failure is False
        assert resp.reject_reason == ""
        assert resp.response_received_at == ""
        assert resp.fill_confirmed_at == ""

    def test_full_fields(self):
        resp = LiveOrderResponse(
            order_id="ord_002",
            order_response_status=OrderResponseStatus.FILLED,
            requested_size=10.0,
            accepted_size=10.0,
            filled_size=10.0,
            remaining_size=0.0,
            fill_confirmed_at="2026-04-02T10:00:00Z",
        )
        assert resp.filled_size == 10.0
        assert resp.remaining_size == 0.0


# ---------------------------------------------------------------------------
# TestFillConfirmation
# ---------------------------------------------------------------------------

class TestFillConfirmation:
    def test_required_fields(self):
        fc = FillConfirmation(
            order_id="ord_001",
            fill_confirmation_status=FillConfirmationStatus.NOT_CONFIRMED,
            requested_size=10.0,
        )
        assert fc.order_id == "ord_001"
        assert fc.fill_confirmation_status == FillConfirmationStatus.NOT_CONFIRMED

    def test_defaults(self):
        fc = FillConfirmation(
            order_id="ord_001",
            fill_confirmation_status=FillConfirmationStatus.NOT_CONFIRMED,
            requested_size=10.0,
        )
        assert fc.filled_size == 0.0
        assert fc.remaining_size == 0.0
        assert fc.fill_confirmed_at == ""


# ---------------------------------------------------------------------------
# TestClassifyOrderResponse
# ---------------------------------------------------------------------------

class TestClassifyOrderResponse:
    def test_default_submitted(self):
        resp = classify_order_response(**base_response())
        assert resp.order_response_status == OrderResponseStatus.SUBMITTED
        assert resp.order_id == "ord_001"

    def test_acknowledged_returns_accepted(self):
        resp = classify_order_response(**base_response(exchange_acknowledged=True))
        assert resp.order_response_status == OrderResponseStatus.ACCEPTED

    def test_partial_fill_returns_partially_filled(self):
        resp = classify_order_response(**base_response(filled_size=5.0))
        assert resp.order_response_status == OrderResponseStatus.PARTIALLY_FILLED

    def test_full_fill_returns_filled(self):
        resp = classify_order_response(**base_response(filled_size=10.0))
        assert resp.order_response_status == OrderResponseStatus.FILLED

    def test_overfill_still_filled(self):
        """filled_size > requested_size → FILLED."""
        resp = classify_order_response(**base_response(filled_size=10.1))
        assert resp.order_response_status == OrderResponseStatus.FILLED

    def test_rejected_returns_rejected(self):
        resp = classify_order_response(**base_response(rejected=True, reject_reason="insufficient_funds"))
        assert resp.order_response_status == OrderResponseStatus.REJECTED
        assert resp.reject_reason == "insufficient_funds"

    def test_retryable_returns_retryable_failure(self):
        resp = classify_order_response(**base_response(retryable=True))
        assert resp.order_response_status == OrderResponseStatus.RETRYABLE_FAILURE
        assert resp.retryable is True

    def test_terminal_returns_terminal_failure(self):
        resp = classify_order_response(**base_response(terminal_failure=True))
        assert resp.order_response_status == OrderResponseStatus.TERMINAL_FAILURE
        assert resp.terminal_failure is True

    def test_terminal_takes_priority_over_retryable(self):
        resp = classify_order_response(**base_response(terminal_failure=True, retryable=True))
        assert resp.order_response_status == OrderResponseStatus.TERMINAL_FAILURE

    def test_retryable_takes_priority_over_rejected(self):
        resp = classify_order_response(**base_response(retryable=True, rejected=True))
        assert resp.order_response_status == OrderResponseStatus.RETRYABLE_FAILURE

    def test_remaining_size_computed(self):
        resp = classify_order_response(**base_response(filled_size=3.0))
        assert resp.remaining_size == 7.0

    def test_fully_filled_remaining_is_zero(self):
        resp = classify_order_response(**base_response(filled_size=10.0))
        assert resp.remaining_size == 0.0

    def test_response_fields_carried(self):
        resp = classify_order_response(
            **base_response(
                accepted_size=10.0,
                response_received_at="2026-04-02T09:00:00Z",
            )
        )
        assert resp.accepted_size == 10.0
        assert resp.response_received_at == "2026-04-02T09:00:00Z"


# ---------------------------------------------------------------------------
# TestBuildFillConfirmation
# ---------------------------------------------------------------------------

class TestBuildFillConfirmation:
    def test_not_filled_returns_not_confirmed(self):
        resp = classify_order_response(**base_response())
        fc = build_fill_confirmation(resp)
        assert fc.fill_confirmation_status == FillConfirmationStatus.NOT_CONFIRMED

    def test_partial_fill_returns_partially_confirmed(self):
        resp = classify_order_response(**base_response(filled_size=4.0))
        fc = build_fill_confirmation(resp)
        assert fc.fill_confirmation_status == FillConfirmationStatus.PARTIALLY_CONFIRMED

    def test_full_fill_returns_fully_confirmed(self):
        resp = classify_order_response(**base_response(filled_size=10.0))
        fc = build_fill_confirmation(resp)
        assert fc.fill_confirmation_status == FillConfirmationStatus.FULLY_CONFIRMED

    def test_terminal_failure_returns_confirmation_failed(self):
        resp = classify_order_response(**base_response(terminal_failure=True))
        fc = build_fill_confirmation(resp)
        assert fc.fill_confirmation_status == FillConfirmationStatus.CONFIRMATION_FAILED

    def test_fill_confirmation_carries_sizes(self):
        resp = classify_order_response(**base_response(filled_size=6.0))
        fc = build_fill_confirmation(resp)
        assert fc.filled_size == 6.0
        assert fc.remaining_size == 4.0
        assert fc.requested_size == 10.0

    def test_fill_confirmation_carries_order_id(self):
        resp = classify_order_response(**base_response(order_id="ord_XYZ"))
        fc = build_fill_confirmation(resp)
        assert fc.order_id == "ord_XYZ"

    def test_fill_confirmed_at_carried(self):
        resp = classify_order_response(**base_response(fill_confirmed_at="2026-04-02T10:30:00Z"))
        fc = build_fill_confirmation(resp)
        assert fc.fill_confirmed_at == "2026-04-02T10:30:00Z"

    def test_submission_seam_not_collapsed(self):
        """LiveOrderResponse and FillConfirmation are separate — not the same object."""
        resp = classify_order_response(**base_response(filled_size=10.0))
        fc = build_fill_confirmation(resp)
        assert type(resp) is LiveOrderResponse
        assert type(fc) is FillConfirmation
