"""Live order submission evaluator — v0.7.3.

Determines whether a live order submission is allowed based on upstream guard results.
Does NOT perform actual order submission or network calls.
Seam only — designed to connect to a live order client in a future version.

Guard priority:
  1. outbound_allowed=False → SUBMISSION_BLOCKED_OUTBOUND_GUARD (v0.7.2 guard failed)
  2. preflight_passed=False → SUBMISSION_BLOCKED_PREFLIGHT (broader preflight failed)
  3. All clear → SUBMISSION_READY (submission_allowed=True, not yet attempted)
"""
from app.domain.live.live_order_request import LiveOrderRequest
from app.domain.live.live_order_result import LiveOrderResult
from app.domain.live.order_submission_status import OrderSubmissionStatus


def evaluate_order_submission(request: LiveOrderRequest) -> LiveOrderResult:
    """Evaluate whether a live order submission is allowed.

    Returns SUBMISSION_READY when all guard conditions pass.
    Returns blocked status with submission_allowed=False otherwise.
    """
    if not request.outbound_allowed:
        return LiveOrderResult(
            submission_allowed=False,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_BLOCKED_OUTBOUND_GUARD,
        )

    if not request.preflight_passed:
        return LiveOrderResult(
            submission_allowed=False,
            order_submission_status=OrderSubmissionStatus.SUBMISSION_BLOCKED_PREFLIGHT,
        )

    return LiveOrderResult(
        submission_allowed=True,
        order_submission_status=OrderSubmissionStatus.SUBMISSION_READY,
    )
