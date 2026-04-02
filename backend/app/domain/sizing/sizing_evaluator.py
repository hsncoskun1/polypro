"""sizing_evaluator — order size evaluation with constraint enforcement."""
from app.domain.sizing.sizing_context import SizingContext
from app.domain.sizing.sizing_mode import SizingMode
from app.domain.sizing.sizing_result import SizingResult


def evaluate_order_size(ctx: SizingContext) -> SizingResult:
    """Evaluate and validate an order size based on sizing mode and policy constraints.

    Evaluation order:
    1. Disallowed sizing mode check
    2. Min available balance to trade check
    3. Raw amount computation (fixed or percent)
    4. Zero / invalid amount check
    5. Insufficient available balance check
    6. Below min order size check
    7. Above max order size check
    8. Normalize and return allowed result
    """
    # 1. Check if sizing mode is allowed by admin policy
    if ctx.sizing_mode.value not in ctx.policy.allowed_sizing_modes:
        return SizingResult(
            size_allowed=False,
            normalized_order_amount=0.0,
            sizing_reason="disallowed_sizing_mode",
        )

    # 2. Check minimum available balance to trade
    if ctx.available_balance < ctx.policy.min_available_balance_to_trade:
        return SizingResult(
            size_allowed=False,
            normalized_order_amount=0.0,
            sizing_reason="below_min_available_balance_to_trade",
        )

    # 3. Compute raw amount based on sizing mode
    if ctx.sizing_mode == SizingMode.FIXED_AMOUNT:
        raw_amount = ctx.fixed_amount
        reason = "sizing_fixed_amount"
    else:  # AVAILABLE_BALANCE_PERCENT
        raw_amount = ctx.available_balance * ctx.available_balance_percent / 100.0
        reason = "sizing_available_balance_percent"

    # 4. Zero / invalid amount check
    if raw_amount <= 0:
        return SizingResult(
            size_allowed=False,
            normalized_order_amount=0.0,
            sizing_reason="normalized_amount_zero_or_invalid",
        )

    # 5. Insufficient available balance check
    if raw_amount > ctx.available_balance:
        return SizingResult(
            size_allowed=False,
            normalized_order_amount=0.0,
            sizing_reason="insufficient_available_balance",
        )

    # 6. Below minimum order size check
    if raw_amount < ctx.policy.min_order_size:
        return SizingResult(
            size_allowed=False,
            normalized_order_amount=0.0,
            sizing_reason="below_min_order_size",
        )

    # 7. Above maximum order size check
    if raw_amount > ctx.policy.max_order_size:
        return SizingResult(
            size_allowed=False,
            normalized_order_amount=0.0,
            sizing_reason="above_max_order_size",
        )

    # 8. Normalize and return
    normalized_amount = round(raw_amount, 2)

    return SizingResult(
        size_allowed=True,
        normalized_order_amount=normalized_amount,
        sizing_reason=reason,
    )
