"""Verification gate evaluator.

Checks ref_valid, market_valid, and settings_ok against VerificationContext.
Fail-closed: trade_allowed is True only when zero blockers remain.

This is a hard-block layer on top of strategy entry decisions.
Even if strategy reports eligible, verification failure blocks the trade.
No soft warnings — every failure is a hard block.
No grace periods.
"""
from app.domain.verification.verification_context import VerificationContext
from app.domain.verification.verification_result import VerificationResult


def evaluate_verification(ctx: VerificationContext) -> VerificationResult:
    """Evaluate pre-trade verification checks and return a gate decision.

    Blocker reasons:
    - ref_invalid       → ref_valid is False
    - market_invalid    → market_valid is False
    - settings_not_ok   → settings_ok is False
    """
    blockers: list[str] = []

    if not ctx.ref_valid:
        blockers.append("ref_invalid")

    if not ctx.market_valid:
        blockers.append("market_invalid")

    if not ctx.settings_ok:
        blockers.append("settings_not_ok")

    return VerificationResult(
        trade_allowed=len(blockers) == 0,
        blocker_reasons=blockers,
    )
