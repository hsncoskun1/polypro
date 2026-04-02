"""Live order cancel/replace evaluator — v0.7.5.

evaluate_cancel(): Determines whether a live cancel is allowed.
evaluate_replace(): Determines whether a live replace/amend is allowed.

Cancel and replace are separate lifecycle intents — never collapsed.
Neither performs actual exchange calls. Seam only.

Guard priority (both cancel and replace):
  1. outbound_allowed=False → BLOCKED_OUTBOUND_GUARD
  2. order_id empty         → BLOCKED_PREFLIGHT (order reference required)
  3. preflight_passed=False → BLOCKED_PREFLIGHT
  4. All clear              → READY
"""
from app.domain.live.cancel_status import CancelStatus
from app.domain.live.live_cancel_request import LiveCancelRequest
from app.domain.live.live_cancel_result import LiveCancelResult
from app.domain.live.live_replace_request import LiveReplaceRequest
from app.domain.live.live_replace_result import LiveReplaceResult
from app.domain.live.replace_status import ReplaceStatus


def evaluate_cancel(request: LiveCancelRequest) -> LiveCancelResult:
    """Evaluate whether a live cancel is allowed."""
    if not request.outbound_allowed:
        return LiveCancelResult(
            cancel_allowed=False,
            cancel_status=CancelStatus.CANCEL_BLOCKED_OUTBOUND_GUARD,
        )
    if not request.order_id:
        return LiveCancelResult(
            cancel_allowed=False,
            cancel_status=CancelStatus.CANCEL_BLOCKED_PREFLIGHT,
        )
    if not request.preflight_passed:
        return LiveCancelResult(
            cancel_allowed=False,
            cancel_status=CancelStatus.CANCEL_BLOCKED_PREFLIGHT,
        )
    return LiveCancelResult(
        cancel_allowed=True,
        cancel_status=CancelStatus.CANCEL_READY,
    )


def evaluate_replace(request: LiveReplaceRequest) -> LiveReplaceResult:
    """Evaluate whether a live replace/amend is allowed."""
    if not request.outbound_allowed:
        return LiveReplaceResult(
            replace_allowed=False,
            replace_status=ReplaceStatus.REPLACE_BLOCKED_OUTBOUND_GUARD,
        )
    if not request.order_id:
        return LiveReplaceResult(
            replace_allowed=False,
            replace_status=ReplaceStatus.REPLACE_BLOCKED_PREFLIGHT,
        )
    if not request.preflight_passed:
        return LiveReplaceResult(
            replace_allowed=False,
            replace_status=ReplaceStatus.REPLACE_BLOCKED_PREFLIGHT,
        )
    return LiveReplaceResult(
        replace_allowed=True,
        replace_status=ReplaceStatus.REPLACE_READY,
    )
