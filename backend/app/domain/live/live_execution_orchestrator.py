"""Live execution orchestrator — v0.7.7.

orchestrate_live_execution(): Maps sub-layer seam statuses to the current
execution stage, determining whether the orchestration is allowed, completed,
retryable, or terminal.

Sub-layer status fields (string values from respective enums):
  submission_status   — OrderSubmissionStatus values (v0.7.3)
  response_status     — OrderResponseStatus values (v0.7.4)
  fill_confirmation_status — FillConfirmationStatus values (v0.7.4)
  cancel_status       — CancelStatus values (v0.7.5)
  replace_status      — ReplaceStatus values (v0.7.5)
  reconciliation_status — ReconciliationStatus values (v0.7.6)

Stage resolution priority:
  1. outbound_allowed=False        → PREFLIGHT_BLOCKED
  2. preflight_passed=False        → PREFLIGHT_BLOCKED
  3. terminal_failure=True         → TERMINAL_FAILURE
  4. retryable=True                → RETRYABLE_FAILURE
  5. reconciliation_status check   → RECONCILED / TERMINAL_FAILURE
  6. fill_confirmation_status check → FILLED / FILL_IN_PROGRESS
  7. cancel_status check           → CANCELLED / CANCEL_IN_PROGRESS
  8. replace_status check          → REPLACED / REPLACE_IN_PROGRESS
  9. response_status present       → RESPONSE_RECEIVED
  10. submission_status == submitted → SUBMITTED
  11. submission_status == ready    → READY_TO_SUBMIT
  12. Default                      → READY_TO_SUBMIT (guards passed, nothing started)

Seam only — no network calls. Does not replace v0.7.3/v0.7.5/v0.7.6 seams.
"""
from app.domain.live.live_execution_orchestration_context import LiveExecutionOrchestrationContext
from app.domain.live.live_execution_orchestration_result import LiveExecutionOrchestrationResult
from app.domain.live.live_execution_stage import LiveExecutionStage


def orchestrate_live_execution(
    ctx: LiveExecutionOrchestrationContext,
) -> LiveExecutionOrchestrationResult:
    """Determine the current live execution stage from sub-layer statuses."""

    # Guard 1: outbound
    if not ctx.outbound_allowed:
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.PREFLIGHT_BLOCKED,
            orchestration_allowed=False,
            blocker_reasons=["outbound_not_allowed"],
        )

    # Guard 2: preflight
    if not ctx.preflight_passed:
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.PREFLIGHT_BLOCKED,
            orchestration_allowed=False,
            blocker_reasons=["preflight_not_passed"],
        )

    # Guard 3: terminal failure (explicit flag from any sub-layer)
    if ctx.terminal_failure:
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.TERMINAL_FAILURE,
            orchestration_allowed=True,
            terminal_failure=True,
        )

    # Guard 4: retryable failure
    if ctx.retryable:
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.RETRYABLE_FAILURE,
            orchestration_allowed=True,
            retryable=True,
        )

    # Stage 5: reconciliation
    if ctx.reconciliation_status == "terminal_state":
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.TERMINAL_FAILURE,
            orchestration_allowed=True,
            terminal_failure=True,
        )
    if ctx.reconciliation_status == "reconciled":
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.RECONCILED,
            orchestration_allowed=True,
            orchestration_completed=True,
        )

    # Stage 6: fill confirmation
    if ctx.fill_confirmation_status == "fully_confirmed":
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.FILLED,
            orchestration_allowed=True,
            orchestration_completed=True,
        )
    if ctx.fill_confirmation_status == "partially_confirmed":
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.FILL_IN_PROGRESS,
            orchestration_allowed=True,
        )

    # Stage 7: cancel
    if ctx.cancel_status == "cancel_cancelled":
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.CANCELLED,
            orchestration_allowed=True,
            orchestration_completed=True,
        )
    if ctx.cancel_status in ("cancel_ready", "cancel_submitted"):
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.CANCEL_IN_PROGRESS,
            orchestration_allowed=True,
        )

    # Stage 8: replace
    if ctx.replace_status == "replace_replaced":
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.REPLACED,
            orchestration_allowed=True,
        )
    if ctx.replace_status in ("replace_ready", "replace_submitted"):
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.REPLACE_IN_PROGRESS,
            orchestration_allowed=True,
        )

    # Stage 9: response received
    if ctx.response_status:
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.RESPONSE_RECEIVED,
            orchestration_allowed=True,
        )

    # Stage 10: submitted
    if ctx.submission_status == "submission_submitted":
        return LiveExecutionOrchestrationResult(
            event_key=ctx.event_key,
            current_stage=LiveExecutionStage.SUBMITTED,
            orchestration_allowed=True,
        )

    # Stage 11 + default: ready to submit
    return LiveExecutionOrchestrationResult(
        event_key=ctx.event_key,
        current_stage=LiveExecutionStage.READY_TO_SUBMIT,
        orchestration_allowed=True,
    )
