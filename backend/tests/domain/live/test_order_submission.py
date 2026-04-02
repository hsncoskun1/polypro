"""Tests for live order submission seam — v0.7.3."""
from app.domain.live.order_submission_status import OrderSubmissionStatus
from app.domain.live.live_order_request import LiveOrderRequest
from app.domain.live.live_order_result import LiveOrderResult
from app.domain.live.order_submission_evaluator import evaluate_order_submission


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def allowed_request(**overrides) -> LiveOrderRequest:
    """All guard conditions passed — submission ready."""
    defaults = dict(
        event_key="evt_001",
        market_id="mkt_btc_usd",
        side="buy",
        requested_size=10.0,
        limit_price=0.75,
        live_mode_requested=True,
        preflight_passed=True,
        outbound_allowed=True,
    )
    defaults.update(overrides)
    return LiveOrderRequest(**defaults)


def blocked_request(**overrides) -> LiveOrderRequest:
    """All guard conditions failed."""
    defaults = dict(
        event_key="evt_001",
        market_id="mkt_btc_usd",
        side="buy",
        requested_size=10.0,
        limit_price=0.75,
        live_mode_requested=False,
        preflight_passed=False,
        outbound_allowed=False,
    )
    defaults.update(overrides)
    return LiveOrderRequest(**defaults)


# ---------------------------------------------------------------------------
# TestOrderSubmissionStatus
# ---------------------------------------------------------------------------

class TestOrderSubmissionStatus:
    def test_allowed_not_attempted_value(self):
        assert OrderSubmissionStatus.SUBMISSION_ALLOWED_NOT_ATTEMPTED == "submission_allowed_not_attempted"

    def test_blocked_preflight_value(self):
        assert OrderSubmissionStatus.SUBMISSION_BLOCKED_PREFLIGHT == "submission_blocked_preflight"

    def test_blocked_outbound_guard_value(self):
        assert OrderSubmissionStatus.SUBMISSION_BLOCKED_OUTBOUND_GUARD == "submission_blocked_outbound_guard"

    def test_ready_value(self):
        assert OrderSubmissionStatus.SUBMISSION_READY == "submission_ready"

    def test_submitted_value(self):
        assert OrderSubmissionStatus.SUBMISSION_SUBMITTED == "submission_submitted"

    def test_rejected_value(self):
        assert OrderSubmissionStatus.SUBMISSION_REJECTED == "submission_rejected"

    def test_retryable_failure_value(self):
        assert OrderSubmissionStatus.SUBMISSION_RETRYABLE_FAILURE == "submission_retryable_failure"

    def test_terminal_failure_value(self):
        assert OrderSubmissionStatus.SUBMISSION_TERMINAL_FAILURE == "submission_terminal_failure"

    def test_is_str_enum(self):
        assert isinstance(OrderSubmissionStatus.SUBMISSION_READY, str)


# ---------------------------------------------------------------------------
# TestLiveOrderRequest
# ---------------------------------------------------------------------------

class TestLiveOrderRequest:
    def test_all_fields_set(self):
        req = allowed_request()
        assert req.event_key == "evt_001"
        assert req.market_id == "mkt_btc_usd"
        assert req.side == "buy"
        assert req.requested_size == 10.0
        assert req.limit_price == 0.75
        assert req.live_mode_requested is True
        assert req.preflight_passed is True
        assert req.outbound_allowed is True

    def test_blocked_request_fields(self):
        req = blocked_request()
        assert req.preflight_passed is False
        assert req.outbound_allowed is False


# ---------------------------------------------------------------------------
# TestLiveOrderResult
# ---------------------------------------------------------------------------

class TestLiveOrderResult:
    def test_ready_result_fields(self):
        result = LiveOrderResult(
            submission_allowed=True,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_READY,
        )
        assert result.submission_allowed is True
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_READY

    def test_blocked_result_fields(self):
        result = LiveOrderResult(
            submission_allowed=False,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_BLOCKED_OUTBOUND_GUARD,
        )
        assert result.submission_allowed is False

    def test_defaults(self):
        result = LiveOrderResult(
            submission_allowed=True,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_READY,
        )
        assert result.order_id == ""
        assert result.reject_reason == ""
        assert result.retryable is False
        assert result.terminal_failure is False
        assert result.submit_attempted_at == ""

    def test_submitted_result_carries_order_id(self):
        result = LiveOrderResult(
            submission_allowed=True,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_SUBMITTED,
            order_id="order_abc123",
            submit_attempted_at="2026-04-02T10:00:00Z",
        )
        assert result.order_id == "order_abc123"
        assert result.submit_attempted_at == "2026-04-02T10:00:00Z"

    def test_rejected_result_carries_reason(self):
        result = LiveOrderResult(
            submission_allowed=False,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_REJECTED,
            reject_reason="insufficient_funds",
        )
        assert result.reject_reason == "insufficient_funds"

    def test_retryable_failure_fields(self):
        result = LiveOrderResult(
            submission_allowed=False,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_RETRYABLE_FAILURE,
            retryable=True,
        )
        assert result.retryable is True
        assert result.terminal_failure is False

    def test_terminal_failure_fields(self):
        result = LiveOrderResult(
            submission_allowed=False,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_TERMINAL_FAILURE,
            terminal_failure=True,
        )
        assert result.terminal_failure is True
        assert result.retryable is False


# ---------------------------------------------------------------------------
# TestOrderSubmissionEvaluator
# ---------------------------------------------------------------------------

class TestOrderSubmissionEvaluator:
    def test_all_clear_returns_ready(self):
        result = evaluate_order_submission(allowed_request())
        assert result.submission_allowed is True
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_READY

    def test_outbound_blocked_returns_blocked_outbound_guard(self):
        req = allowed_request(outbound_allowed=False)
        result = evaluate_order_submission(req)
        assert result.submission_allowed is False
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_BLOCKED_OUTBOUND_GUARD

    def test_preflight_failed_returns_blocked_preflight(self):
        req = allowed_request(preflight_passed=False)
        result = evaluate_order_submission(req)
        assert result.submission_allowed is False
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_BLOCKED_PREFLIGHT

    def test_outbound_guard_takes_priority_over_preflight(self):
        """outbound_allowed=False must be caught before preflight_passed=False."""
        req = allowed_request(outbound_allowed=False, preflight_passed=False)
        result = evaluate_order_submission(req)
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_BLOCKED_OUTBOUND_GUARD

    def test_simulation_mode_blocked_via_outbound_guard(self):
        """Simulation mode blocks outbound — evaluator sees outbound_allowed=False."""
        req = blocked_request(outbound_allowed=False)
        result = evaluate_order_submission(req)
        assert result.submission_allowed is False
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_BLOCKED_OUTBOUND_GUARD

    def test_no_live_mode_blocked_via_preflight(self):
        """No live mode → preflight fails → SUBMISSION_BLOCKED_PREFLIGHT."""
        req = allowed_request(outbound_allowed=True, preflight_passed=False)
        result = evaluate_order_submission(req)
        assert result.submission_allowed is False
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_BLOCKED_PREFLIGHT

    def test_ready_result_has_no_reject_reason(self):
        result = evaluate_order_submission(allowed_request())
        assert result.reject_reason == ""
        assert result.order_id == ""

    def test_request_fields_preserved(self):
        """Request data is accessible on the request object in all scenarios."""
        req = allowed_request(event_key="evt_XYZ", market_id="mkt_eth", requested_size=50.0)
        result = evaluate_order_submission(req)
        assert req.event_key == "evt_XYZ"
        assert req.market_id == "mkt_eth"
        assert req.requested_size == 50.0
        assert result.submission_allowed is True

    def test_ready_integrates_with_preflight_evaluator(self):
        """Full chain: PreflightContext → evaluate_preflight → LiveOrderRequest → evaluate_order_submission."""
        from app.domain.live.preflight_context import PreflightContext
        from app.domain.live.outbound_action_type import OutboundActionType
        from app.domain.live.preflight_evaluator import evaluate_preflight

        ctx = PreflightContext(
            simulation_mode_default=False,
            live_mode_requested=True,
            live_mode_enabled=True,
            explicit_live_enable=True,
            credentials_complete=True,
            verification_passed=True,
            sizing_passed=True,
            risk_passed=True,
            outbound_action_type=OutboundActionType.LIVE_ORDER_SUBMIT,
        )
        preflight_result = evaluate_preflight(ctx)
        req = LiveOrderRequest(
            event_key="evt_001",
            market_id="mkt_abc",
            side="buy",
            requested_size=10.0,
            limit_price=0.65,
            live_mode_requested=True,
            preflight_passed=preflight_result.outbound_allowed,
            outbound_allowed=preflight_result.outbound_allowed,
        )
        result = evaluate_order_submission(req)
        assert result.submission_allowed is True
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_READY

    def test_blocked_chain_simulation_to_submission(self):
        """Full chain: simulation preflight → blocked outbound → blocked submission."""
        from app.domain.live.preflight_context import PreflightContext
        from app.domain.live.outbound_action_type import OutboundActionType
        from app.domain.live.preflight_evaluator import evaluate_preflight

        ctx = PreflightContext(
            simulation_mode_default=True,
            live_mode_requested=False,
            live_mode_enabled=False,
            explicit_live_enable=False,
            credentials_complete=False,
            verification_passed=False,
            sizing_passed=False,
            risk_passed=False,
            outbound_action_type=OutboundActionType.LIVE_ORDER_SUBMIT,
        )
        preflight_result = evaluate_preflight(ctx)
        req = LiveOrderRequest(
            event_key="evt_001",
            market_id="mkt_abc",
            side="buy",
            requested_size=10.0,
            limit_price=0.65,
            live_mode_requested=False,
            preflight_passed=preflight_result.outbound_allowed,
            outbound_allowed=preflight_result.outbound_allowed,
        )
        result = evaluate_order_submission(req)
        assert result.submission_allowed is False
        assert result.order_submission_status == OrderSubmissionStatus.SUBMISSION_BLOCKED_OUTBOUND_GUARD
