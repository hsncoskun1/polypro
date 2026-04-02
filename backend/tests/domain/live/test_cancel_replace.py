"""Tests for live order cancel/replace seam — v0.7.5."""
from app.domain.live.cancel_status import CancelStatus
from app.domain.live.replace_status import ReplaceStatus
from app.domain.live.live_cancel_request import LiveCancelRequest
from app.domain.live.live_cancel_result import LiveCancelResult
from app.domain.live.live_replace_request import LiveReplaceRequest
from app.domain.live.live_replace_result import LiveReplaceResult
from app.domain.live.cancel_replace_evaluator import evaluate_cancel, evaluate_replace


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def allowed_cancel(**overrides) -> LiveCancelRequest:
    defaults = dict(order_id="ord_001", outbound_allowed=True, preflight_passed=True)
    defaults.update(overrides)
    return LiveCancelRequest(**defaults)


def allowed_replace(**overrides) -> LiveReplaceRequest:
    defaults = dict(
        order_id="ord_001",
        new_limit_price=0.75,
        new_size=10.0,
        outbound_allowed=True,
        preflight_passed=True,
    )
    defaults.update(overrides)
    return LiveReplaceRequest(**defaults)


# ---------------------------------------------------------------------------
# TestCancelStatus
# ---------------------------------------------------------------------------

class TestCancelStatus:
    def test_allowed_not_attempted(self):
        assert CancelStatus.CANCEL_ALLOWED_NOT_ATTEMPTED == "cancel_allowed_not_attempted"

    def test_blocked_preflight(self):
        assert CancelStatus.CANCEL_BLOCKED_PREFLIGHT == "cancel_blocked_preflight"

    def test_blocked_outbound_guard(self):
        assert CancelStatus.CANCEL_BLOCKED_OUTBOUND_GUARD == "cancel_blocked_outbound_guard"

    def test_ready(self):
        assert CancelStatus.CANCEL_READY == "cancel_ready"

    def test_submitted(self):
        assert CancelStatus.CANCEL_SUBMITTED == "cancel_submitted"

    def test_rejected(self):
        assert CancelStatus.CANCEL_REJECTED == "cancel_rejected"

    def test_retryable_failure(self):
        assert CancelStatus.CANCEL_RETRYABLE_FAILURE == "cancel_retryable_failure"

    def test_terminal_failure(self):
        assert CancelStatus.CANCEL_TERMINAL_FAILURE == "cancel_terminal_failure"

    def test_is_str_enum(self):
        assert isinstance(CancelStatus.CANCEL_READY, str)


# ---------------------------------------------------------------------------
# TestReplaceStatus
# ---------------------------------------------------------------------------

class TestReplaceStatus:
    def test_allowed_not_attempted(self):
        assert ReplaceStatus.REPLACE_ALLOWED_NOT_ATTEMPTED == "replace_allowed_not_attempted"

    def test_blocked_preflight(self):
        assert ReplaceStatus.REPLACE_BLOCKED_PREFLIGHT == "replace_blocked_preflight"

    def test_blocked_outbound_guard(self):
        assert ReplaceStatus.REPLACE_BLOCKED_OUTBOUND_GUARD == "replace_blocked_outbound_guard"

    def test_ready(self):
        assert ReplaceStatus.REPLACE_READY == "replace_ready"

    def test_submitted(self):
        assert ReplaceStatus.REPLACE_SUBMITTED == "replace_submitted"

    def test_rejected(self):
        assert ReplaceStatus.REPLACE_REJECTED == "replace_rejected"

    def test_retryable_failure(self):
        assert ReplaceStatus.REPLACE_RETRYABLE_FAILURE == "replace_retryable_failure"

    def test_terminal_failure(self):
        assert ReplaceStatus.REPLACE_TERMINAL_FAILURE == "replace_terminal_failure"

    def test_is_str_enum(self):
        assert isinstance(ReplaceStatus.REPLACE_READY, str)


# ---------------------------------------------------------------------------
# TestLiveCancelResult
# ---------------------------------------------------------------------------

class TestLiveCancelResult:
    def test_ready_result_fields(self):
        r = LiveCancelResult(cancel_allowed=True, cancel_status=CancelStatus.CANCEL_READY)
        assert r.cancel_allowed is True
        assert r.cancel_status == CancelStatus.CANCEL_READY

    def test_defaults(self):
        r = LiveCancelResult(cancel_allowed=True, cancel_status=CancelStatus.CANCEL_READY)
        assert r.reject_reason == ""
        assert r.retryable is False
        assert r.terminal_failure is False
        assert r.cancel_attempted_at == ""

    def test_rejected_carries_reason(self):
        r = LiveCancelResult(
            cancel_allowed=False,
            cancel_status=CancelStatus.CANCEL_REJECTED,
            reject_reason="already_cancelled",
        )
        assert r.reject_reason == "already_cancelled"

    def test_retryable_fields(self):
        r = LiveCancelResult(
            cancel_allowed=False,
            cancel_status=CancelStatus.CANCEL_RETRYABLE_FAILURE,
            retryable=True,
        )
        assert r.retryable is True
        assert r.terminal_failure is False

    def test_terminal_fields(self):
        r = LiveCancelResult(
            cancel_allowed=False,
            cancel_status=CancelStatus.CANCEL_TERMINAL_FAILURE,
            terminal_failure=True,
        )
        assert r.terminal_failure is True
        assert r.retryable is False


# ---------------------------------------------------------------------------
# TestLiveReplaceResult
# ---------------------------------------------------------------------------

class TestLiveReplaceResult:
    def test_ready_result_fields(self):
        r = LiveReplaceResult(replace_allowed=True, replace_status=ReplaceStatus.REPLACE_READY)
        assert r.replace_allowed is True
        assert r.replace_status == ReplaceStatus.REPLACE_READY

    def test_defaults(self):
        r = LiveReplaceResult(replace_allowed=True, replace_status=ReplaceStatus.REPLACE_READY)
        assert r.replace_reason == ""
        assert r.retryable is False
        assert r.terminal_failure is False
        assert r.replace_attempted_at == ""


# ---------------------------------------------------------------------------
# TestEvaluateCancel
# ---------------------------------------------------------------------------

class TestEvaluateCancel:
    def test_all_clear_returns_cancel_ready(self):
        result = evaluate_cancel(allowed_cancel())
        assert result.cancel_allowed is True
        assert result.cancel_status == CancelStatus.CANCEL_READY

    def test_outbound_blocked_returns_blocked_outbound_guard(self):
        result = evaluate_cancel(allowed_cancel(outbound_allowed=False))
        assert result.cancel_allowed is False
        assert result.cancel_status == CancelStatus.CANCEL_BLOCKED_OUTBOUND_GUARD

    def test_preflight_failed_returns_blocked_preflight(self):
        result = evaluate_cancel(allowed_cancel(preflight_passed=False))
        assert result.cancel_allowed is False
        assert result.cancel_status == CancelStatus.CANCEL_BLOCKED_PREFLIGHT

    def test_missing_order_id_returns_blocked_preflight(self):
        result = evaluate_cancel(allowed_cancel(order_id=""))
        assert result.cancel_allowed is False
        assert result.cancel_status == CancelStatus.CANCEL_BLOCKED_PREFLIGHT

    def test_outbound_guard_takes_priority_over_missing_order_id(self):
        result = evaluate_cancel(allowed_cancel(outbound_allowed=False, order_id=""))
        assert result.cancel_status == CancelStatus.CANCEL_BLOCKED_OUTBOUND_GUARD

    def test_outbound_guard_takes_priority_over_preflight(self):
        result = evaluate_cancel(allowed_cancel(outbound_allowed=False, preflight_passed=False))
        assert result.cancel_status == CancelStatus.CANCEL_BLOCKED_OUTBOUND_GUARD

    def test_simulation_blocked_via_outbound_guard(self):
        """Simulation mode results in outbound_allowed=False — cancel blocked."""
        result = evaluate_cancel(allowed_cancel(outbound_allowed=False))
        assert result.cancel_status == CancelStatus.CANCEL_BLOCKED_OUTBOUND_GUARD

    def test_cancel_and_replace_are_separate(self):
        """Cancel evaluator must not use ReplaceStatus."""
        result = evaluate_cancel(allowed_cancel())
        assert isinstance(result.cancel_status, CancelStatus)


# ---------------------------------------------------------------------------
# TestEvaluateReplace
# ---------------------------------------------------------------------------

class TestEvaluateReplace:
    def test_all_clear_returns_replace_ready(self):
        result = evaluate_replace(allowed_replace())
        assert result.replace_allowed is True
        assert result.replace_status == ReplaceStatus.REPLACE_READY

    def test_outbound_blocked_returns_blocked_outbound_guard(self):
        result = evaluate_replace(allowed_replace(outbound_allowed=False))
        assert result.replace_allowed is False
        assert result.replace_status == ReplaceStatus.REPLACE_BLOCKED_OUTBOUND_GUARD

    def test_preflight_failed_returns_blocked_preflight(self):
        result = evaluate_replace(allowed_replace(preflight_passed=False))
        assert result.replace_allowed is False
        assert result.replace_status == ReplaceStatus.REPLACE_BLOCKED_PREFLIGHT

    def test_missing_order_id_returns_blocked_preflight(self):
        result = evaluate_replace(allowed_replace(order_id=""))
        assert result.replace_allowed is False
        assert result.replace_status == ReplaceStatus.REPLACE_BLOCKED_PREFLIGHT

    def test_outbound_guard_takes_priority_over_missing_order_id(self):
        result = evaluate_replace(allowed_replace(outbound_allowed=False, order_id=""))
        assert result.replace_status == ReplaceStatus.REPLACE_BLOCKED_OUTBOUND_GUARD

    def test_simulation_blocked_via_outbound_guard(self):
        result = evaluate_replace(allowed_replace(outbound_allowed=False))
        assert result.replace_status == ReplaceStatus.REPLACE_BLOCKED_OUTBOUND_GUARD

    def test_replace_carries_new_fields(self):
        req = allowed_replace(new_limit_price=0.85, new_size=20.0)
        result = evaluate_replace(req)
        assert req.new_limit_price == 0.85
        assert req.new_size == 20.0
        assert result.replace_allowed is True

    def test_replace_and_cancel_are_separate(self):
        """Replace evaluator must not use CancelStatus."""
        result = evaluate_replace(allowed_replace())
        assert isinstance(result.replace_status, ReplaceStatus)

    def test_cancel_replace_not_collapsed(self):
        """Cancel and replace return different result types."""
        cancel_result = evaluate_cancel(allowed_cancel())
        replace_result = evaluate_replace(allowed_replace())
        assert type(cancel_result) is LiveCancelResult
        assert type(replace_result) is LiveReplaceResult
