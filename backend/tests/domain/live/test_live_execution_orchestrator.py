"""Tests for live execution orchestrator foundation — v0.7.7."""
from app.domain.live.live_execution_stage import LiveExecutionStage
from app.domain.live.live_execution_orchestration_context import LiveExecutionOrchestrationContext
from app.domain.live.live_execution_orchestration_result import LiveExecutionOrchestrationResult
from app.domain.live.live_execution_orchestrator import orchestrate_live_execution


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def base_ctx(**overrides) -> LiveExecutionOrchestrationContext:
    defaults = dict(
        event_key="evt_001",
        order_id="ord_001",
        live_mode_requested=True,
        outbound_allowed=True,
        preflight_passed=True,
    )
    defaults.update(overrides)
    return LiveExecutionOrchestrationContext(**defaults)


# ---------------------------------------------------------------------------
# TestLiveExecutionStage
# ---------------------------------------------------------------------------

class TestLiveExecutionStage:
    def test_preflight_blocked(self):
        assert LiveExecutionStage.PREFLIGHT_BLOCKED == "preflight_blocked"

    def test_ready_to_submit(self):
        assert LiveExecutionStage.READY_TO_SUBMIT == "ready_to_submit"

    def test_submitted(self):
        assert LiveExecutionStage.SUBMITTED == "submitted"

    def test_response_received(self):
        assert LiveExecutionStage.RESPONSE_RECEIVED == "response_received"

    def test_fill_in_progress(self):
        assert LiveExecutionStage.FILL_IN_PROGRESS == "fill_in_progress"

    def test_filled(self):
        assert LiveExecutionStage.FILLED == "filled"

    def test_cancel_in_progress(self):
        assert LiveExecutionStage.CANCEL_IN_PROGRESS == "cancel_in_progress"

    def test_cancelled(self):
        assert LiveExecutionStage.CANCELLED == "cancelled"

    def test_replace_in_progress(self):
        assert LiveExecutionStage.REPLACE_IN_PROGRESS == "replace_in_progress"

    def test_replaced(self):
        assert LiveExecutionStage.REPLACED == "replaced"

    def test_reconciled(self):
        assert LiveExecutionStage.RECONCILED == "reconciled"

    def test_retryable_failure(self):
        assert LiveExecutionStage.RETRYABLE_FAILURE == "retryable_failure"

    def test_terminal_failure(self):
        assert LiveExecutionStage.TERMINAL_FAILURE == "terminal_failure"

    def test_is_str_enum(self):
        assert isinstance(LiveExecutionStage.READY_TO_SUBMIT, str)


# ---------------------------------------------------------------------------
# TestLiveExecutionOrchestrationContext
# ---------------------------------------------------------------------------

class TestLiveExecutionOrchestrationContext:
    def test_required_fields(self):
        ctx = LiveExecutionOrchestrationContext(event_key="evt_001")
        assert ctx.event_key == "evt_001"

    def test_defaults(self):
        ctx = LiveExecutionOrchestrationContext(event_key="evt_001")
        assert ctx.order_id == ""
        assert ctx.live_mode_requested is False
        assert ctx.outbound_allowed is False
        assert ctx.preflight_passed is False
        assert ctx.submission_status == ""
        assert ctx.response_status == ""
        assert ctx.fill_confirmation_status == ""
        assert ctx.cancel_status == ""
        assert ctx.replace_status == ""
        assert ctx.reconciliation_status == ""
        assert ctx.terminal_failure is False
        assert ctx.retryable is False


# ---------------------------------------------------------------------------
# TestLiveExecutionOrchestrationResult
# ---------------------------------------------------------------------------

class TestLiveExecutionOrchestrationResult:
    def test_required_fields(self):
        r = LiveExecutionOrchestrationResult(
            event_key="evt_001",
            current_stage=LiveExecutionStage.READY_TO_SUBMIT,
            orchestration_allowed=True,
        )
        assert r.event_key == "evt_001"
        assert r.current_stage == LiveExecutionStage.READY_TO_SUBMIT
        assert r.orchestration_allowed is True

    def test_defaults(self):
        r = LiveExecutionOrchestrationResult(
            event_key="evt_001",
            current_stage=LiveExecutionStage.READY_TO_SUBMIT,
            orchestration_allowed=True,
        )
        assert r.orchestration_completed is False
        assert r.retryable is False
        assert r.terminal_failure is False
        assert r.blocker_reasons == []


# ---------------------------------------------------------------------------
# TestOrchestrateGuards
# ---------------------------------------------------------------------------

class TestOrchestrateGuards:
    def test_outbound_blocked_returns_preflight_blocked(self):
        result = orchestrate_live_execution(base_ctx(outbound_allowed=False))
        assert result.current_stage == LiveExecutionStage.PREFLIGHT_BLOCKED
        assert result.orchestration_allowed is False

    def test_outbound_blocked_carries_blocker_reason(self):
        result = orchestrate_live_execution(base_ctx(outbound_allowed=False))
        assert "outbound_not_allowed" in result.blocker_reasons

    def test_preflight_not_passed_returns_preflight_blocked(self):
        result = orchestrate_live_execution(base_ctx(preflight_passed=False))
        assert result.current_stage == LiveExecutionStage.PREFLIGHT_BLOCKED
        assert result.orchestration_allowed is False

    def test_preflight_blocked_carries_blocker_reason(self):
        result = orchestrate_live_execution(base_ctx(preflight_passed=False))
        assert "preflight_not_passed" in result.blocker_reasons

    def test_outbound_guard_takes_priority_over_preflight(self):
        result = orchestrate_live_execution(
            base_ctx(outbound_allowed=False, preflight_passed=False)
        )
        assert result.current_stage == LiveExecutionStage.PREFLIGHT_BLOCKED
        assert "outbound_not_allowed" in result.blocker_reasons

    def test_terminal_failure_flag_returns_terminal_stage(self):
        result = orchestrate_live_execution(base_ctx(terminal_failure=True))
        assert result.current_stage == LiveExecutionStage.TERMINAL_FAILURE
        assert result.terminal_failure is True

    def test_retryable_flag_returns_retryable_stage(self):
        result = orchestrate_live_execution(base_ctx(retryable=True))
        assert result.current_stage == LiveExecutionStage.RETRYABLE_FAILURE
        assert result.retryable is True

    def test_terminal_takes_priority_over_retryable(self):
        result = orchestrate_live_execution(base_ctx(terminal_failure=True, retryable=True))
        assert result.current_stage == LiveExecutionStage.TERMINAL_FAILURE


# ---------------------------------------------------------------------------
# TestOrchestrateStages
# ---------------------------------------------------------------------------

class TestOrchestrateStages:
    def test_all_clear_no_sub_status_returns_ready_to_submit(self):
        result = orchestrate_live_execution(base_ctx())
        assert result.current_stage == LiveExecutionStage.READY_TO_SUBMIT
        assert result.orchestration_allowed is True

    def test_submission_ready_returns_ready_to_submit(self):
        result = orchestrate_live_execution(base_ctx(submission_status="submission_ready"))
        assert result.current_stage == LiveExecutionStage.READY_TO_SUBMIT

    def test_submission_submitted_returns_submitted(self):
        result = orchestrate_live_execution(base_ctx(submission_status="submission_submitted"))
        assert result.current_stage == LiveExecutionStage.SUBMITTED

    def test_response_received_returns_response_received(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                response_status="accepted",
            )
        )
        assert result.current_stage == LiveExecutionStage.RESPONSE_RECEIVED

    def test_partial_fill_returns_fill_in_progress(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                response_status="partially_filled",
                fill_confirmation_status="partially_confirmed",
            )
        )
        assert result.current_stage == LiveExecutionStage.FILL_IN_PROGRESS

    def test_full_fill_returns_filled(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                response_status="filled",
                fill_confirmation_status="fully_confirmed",
            )
        )
        assert result.current_stage == LiveExecutionStage.FILLED
        assert result.orchestration_completed is True

    def test_cancel_ready_returns_cancel_in_progress(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                cancel_status="cancel_ready",
            )
        )
        assert result.current_stage == LiveExecutionStage.CANCEL_IN_PROGRESS

    def test_cancel_submitted_returns_cancel_in_progress(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                cancel_status="cancel_submitted",
            )
        )
        assert result.current_stage == LiveExecutionStage.CANCEL_IN_PROGRESS

    def test_cancelled_returns_cancelled(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                cancel_status="cancel_cancelled",
            )
        )
        assert result.current_stage == LiveExecutionStage.CANCELLED
        assert result.orchestration_completed is True

    def test_replace_ready_returns_replace_in_progress(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                replace_status="replace_ready",
            )
        )
        assert result.current_stage == LiveExecutionStage.REPLACE_IN_PROGRESS

    def test_replace_submitted_returns_replace_in_progress(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                replace_status="replace_submitted",
            )
        )
        assert result.current_stage == LiveExecutionStage.REPLACE_IN_PROGRESS

    def test_replaced_returns_replaced(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                replace_status="replace_replaced",
            )
        )
        assert result.current_stage == LiveExecutionStage.REPLACED

    def test_reconciled_returns_reconciled(self):
        result = orchestrate_live_execution(
            base_ctx(
                submission_status="submission_submitted",
                response_status="filled",
                fill_confirmation_status="fully_confirmed",
                reconciliation_status="reconciled",
            )
        )
        assert result.current_stage == LiveExecutionStage.RECONCILED
        assert result.orchestration_completed is True

    def test_reconciliation_terminal_returns_terminal_failure(self):
        result = orchestrate_live_execution(
            base_ctx(reconciliation_status="terminal_state")
        )
        assert result.current_stage == LiveExecutionStage.TERMINAL_FAILURE
        assert result.terminal_failure is True

    def test_event_key_preserved(self):
        result = orchestrate_live_execution(base_ctx(event_key="evt_xyz"))
        assert result.event_key == "evt_xyz"

    def test_sub_layer_statuses_not_collapsed(self):
        """Cancel and replace remain distinct stages — orchestrator never collapses them."""
        cancel_result = orchestrate_live_execution(
            base_ctx(submission_status="submission_submitted", cancel_status="cancel_cancelled")
        )
        replace_result = orchestrate_live_execution(
            base_ctx(submission_status="submission_submitted", replace_status="replace_replaced")
        )
        assert cancel_result.current_stage == LiveExecutionStage.CANCELLED
        assert replace_result.current_stage == LiveExecutionStage.REPLACED
        assert cancel_result.current_stage != replace_result.current_stage

    def test_simulation_blocked_via_outbound_guard(self):
        """Simulation mode results in outbound_allowed=False — orchestration blocked."""
        result = orchestrate_live_execution(base_ctx(outbound_allowed=False))
        assert result.current_stage == LiveExecutionStage.PREFLIGHT_BLOCKED
        assert result.orchestration_allowed is False
