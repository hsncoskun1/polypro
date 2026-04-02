"""claim_evaluator — claim/settlement state evaluation."""
from app.domain.claim.claim_context import ClaimContext
from app.domain.claim.claim_result import ClaimResult
from app.domain.claim.claim_status import ClaimStatus


def evaluate_claim_state(ctx: ClaimContext) -> ClaimResult:
    """Evaluate claim/settlement state from context.

    Gate order:
    1. event_outcome_known — outcome must be known before anything proceeds
    2. resolution_finalized — resolution must be finalized before claim is possible
    3. claim_available — platform must have made claim available
    4. claim_failed — failed state checked before submitted/completed
    5. claim_completed — terminal success state
    6. claim_submitted — in-flight state
    7. default — claim is available to submit

    balance_after_claim is computed only when claim_completed.
    early_exit_realized_pnl and settlement_effect are always carried separately.
    """
    # Gate 1: Outcome unknown
    if not ctx.event_outcome_known:
        return _blocked(
            status=ClaimStatus.NOT_CLAIMABLE_OUTCOME_UNKNOWN,
            ctx=ctx,
        )

    # Gate 2: Resolution not yet finalized
    if not ctx.resolution_finalized:
        return _blocked(
            status=ClaimStatus.NOT_CLAIMABLE_RESOLUTION_PENDING,
            ctx=ctx,
        )

    # Gate 3: Claim not yet available on platform
    if not ctx.claim_available:
        return _blocked(
            status=ClaimStatus.NOT_CLAIMABLE_CLAIM_UNAVAILABLE,
            ctx=ctx,
        )

    # Claim gate passed — determine lifecycle state

    # Claim failed
    if ctx.claim_failed:
        return _result(
            status=ClaimStatus.CLAIM_FAILED,
            is_claimable=False,
            ctx=ctx,
        )

    # Claim completed — compute balance_after_claim
    if ctx.claim_completed:
        balance_after_claim = (
            ctx.balance_before_claim
            + ctx.claimed_amount
            + ctx.claim_adjusted_balance_effect
        )
        return ClaimResult(
            claim_status=ClaimStatus.CLAIM_COMPLETED,
            is_claimable=False,
            balance_after_claim=balance_after_claim,
            claimed_amount=ctx.claimed_amount,
            claim_adjusted_balance_effect=ctx.claim_adjusted_balance_effect,
            early_exit_realized_pnl=ctx.early_exit_realized_pnl,
            settlement_effect=ctx.settlement_effect,
            settlement_completed_at=ctx.settlement_completed_at,
        )

    # Claim submitted but not yet resolved
    if ctx.claim_submitted:
        return _result(
            status=ClaimStatus.CLAIM_SUBMITTED,
            is_claimable=False,
            ctx=ctx,
        )

    # Default — claim is available to submit
    return _result(
        status=ClaimStatus.CLAIM_AVAILABLE,
        is_claimable=True,
        ctx=ctx,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _blocked(status: ClaimStatus, ctx: ClaimContext) -> ClaimResult:
    """Return a blocked result — balance unchanged, not claimable."""
    return ClaimResult(
        claim_status=status,
        is_claimable=False,
        balance_after_claim=ctx.balance_before_claim,
        claimed_amount=ctx.claimed_amount,
        claim_adjusted_balance_effect=ctx.claim_adjusted_balance_effect,
        early_exit_realized_pnl=ctx.early_exit_realized_pnl,
        settlement_effect=ctx.settlement_effect,
        settlement_completed_at=ctx.settlement_completed_at,
    )


def _result(status: ClaimStatus, is_claimable: bool, ctx: ClaimContext) -> ClaimResult:
    """Return a result — balance unchanged (claim not completed)."""
    return ClaimResult(
        claim_status=status,
        is_claimable=is_claimable,
        balance_after_claim=ctx.balance_before_claim,
        claimed_amount=ctx.claimed_amount,
        claim_adjusted_balance_effect=ctx.claim_adjusted_balance_effect,
        early_exit_realized_pnl=ctx.early_exit_realized_pnl,
        settlement_effect=ctx.settlement_effect,
        settlement_completed_at=ctx.settlement_completed_at,
    )
