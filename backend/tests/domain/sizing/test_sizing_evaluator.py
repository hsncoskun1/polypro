"""Tests for order sizing evaluation — v0.5.5."""
import pytest
from app.domain.sizing.sizing_mode import SizingMode
from app.domain.sizing.sizing_policy import SizingPolicy
from app.domain.sizing.sizing_context import SizingContext
from app.domain.sizing.sizing_result import SizingResult
from app.domain.sizing.sizing_evaluator import evaluate_order_size


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def default_policy(
    min_order_size: float = 1.0,
    max_order_size: float = 500.0,
    min_available_balance_to_trade: float = 5.0,
    allowed_sizing_modes=None,
) -> SizingPolicy:
    if allowed_sizing_modes is None:
        allowed_sizing_modes = ["fixed_amount", "available_balance_percent"]
    return SizingPolicy(
        min_order_size=min_order_size,
        max_order_size=max_order_size,
        min_available_balance_to_trade=min_available_balance_to_trade,
        allowed_sizing_modes=allowed_sizing_modes,
    )


# ---------------------------------------------------------------------------
# TestSizingMode
# ---------------------------------------------------------------------------

class TestSizingMode:
    def test_fixed_amount_value(self):
        assert SizingMode.FIXED_AMOUNT.value == "fixed_amount"

    def test_available_balance_percent_value(self):
        assert SizingMode.AVAILABLE_BALANCE_PERCENT.value == "available_balance_percent"

    def test_from_string(self):
        assert SizingMode("fixed_amount") == SizingMode.FIXED_AMOUNT

    def test_modes_are_distinct(self):
        assert SizingMode.FIXED_AMOUNT != SizingMode.AVAILABLE_BALANCE_PERCENT


# ---------------------------------------------------------------------------
# TestSizingResult
# ---------------------------------------------------------------------------

class TestSizingResult:
    def test_allowed_result_fields(self):
        result = SizingResult(
            size_allowed=True,
            normalized_order_amount=25.0,
            sizing_reason="sizing_fixed_amount",
        )
        assert result.size_allowed is True
        assert result.normalized_order_amount == 25.0
        assert result.sizing_reason == "sizing_fixed_amount"

    def test_blocked_result_fields(self):
        result = SizingResult(
            size_allowed=False,
            normalized_order_amount=0.0,
            sizing_reason="below_min_order_size",
        )
        assert result.size_allowed is False
        assert result.normalized_order_amount == 0.0


# ---------------------------------------------------------------------------
# TestEvaluateOrderSizeFixed
# ---------------------------------------------------------------------------

class TestEvaluateOrderSizeFixed:
    def test_fixed_amount_produces_correct_amount(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=100.0,
            total_balance=200.0,
            policy=default_policy(),
            fixed_amount=25.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is True
        assert result.normalized_order_amount == 25.0
        assert result.sizing_reason == "sizing_fixed_amount"

    def test_fixed_amount_reason_is_sizing_fixed_amount(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=200.0,
            total_balance=200.0,
            policy=default_policy(),
            fixed_amount=50.0,
        )
        result = evaluate_order_size(ctx)
        assert result.sizing_reason == "sizing_fixed_amount"

    def test_fixed_amount_normalized_to_two_decimal_places(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(),
            fixed_amount=10.555,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is True
        assert result.normalized_order_amount == round(10.555, 2)

    def test_fixed_amount_zero_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(),
            fixed_amount=0.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "normalized_amount_zero_or_invalid"

    def test_fixed_amount_negative_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(),
            fixed_amount=-10.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "normalized_amount_zero_or_invalid"


# ---------------------------------------------------------------------------
# TestEvaluateOrderSizePercent
# ---------------------------------------------------------------------------

class TestEvaluateOrderSizePercent:
    def test_percent_sizing_produces_correct_amount(self):
        # 20% of 100.0 = 20.0
        ctx = SizingContext(
            sizing_mode=SizingMode.AVAILABLE_BALANCE_PERCENT,
            available_balance=100.0,
            total_balance=200.0,
            policy=default_policy(),
            available_balance_percent=20.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is True
        assert result.normalized_order_amount == 20.0
        assert result.sizing_reason == "sizing_available_balance_percent"

    def test_percent_sizing_reason_is_correct(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.AVAILABLE_BALANCE_PERCENT,
            available_balance=200.0,
            total_balance=200.0,
            policy=default_policy(),
            available_balance_percent=10.0,
        )
        result = evaluate_order_size(ctx)
        assert result.sizing_reason == "sizing_available_balance_percent"

    def test_percent_zero_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.AVAILABLE_BALANCE_PERCENT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(),
            available_balance_percent=0.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "normalized_amount_zero_or_invalid"

    def test_percent_50_of_200_produces_100(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.AVAILABLE_BALANCE_PERCENT,
            available_balance=200.0,
            total_balance=200.0,
            policy=default_policy(max_order_size=200.0),
            available_balance_percent=50.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is True
        assert result.normalized_order_amount == 100.0


# ---------------------------------------------------------------------------
# TestEvaluateOrderSizeConstraints
# ---------------------------------------------------------------------------

class TestEvaluateOrderSizeConstraints:
    def test_below_min_order_size_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(min_order_size=10.0),
            fixed_amount=5.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "below_min_order_size"
        assert result.normalized_order_amount == 0.0

    def test_above_max_order_size_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=1000.0,
            total_balance=1000.0,
            policy=default_policy(max_order_size=100.0),
            fixed_amount=200.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "above_max_order_size"
        assert result.normalized_order_amount == 0.0

    def test_insufficient_available_balance_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=30.0,
            total_balance=100.0,
            policy=default_policy(),
            fixed_amount=50.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "insufficient_available_balance"

    def test_below_min_available_balance_to_trade_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=3.0,
            total_balance=100.0,
            policy=default_policy(min_available_balance_to_trade=5.0),
            fixed_amount=2.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "below_min_available_balance_to_trade"

    def test_disallowed_sizing_mode_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.AVAILABLE_BALANCE_PERCENT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(allowed_sizing_modes=["fixed_amount"]),
            available_balance_percent=10.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "disallowed_sizing_mode"

    def test_disallowed_sizing_mode_fixed_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(allowed_sizing_modes=["available_balance_percent"]),
            fixed_amount=10.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "disallowed_sizing_mode"

    def test_normalized_amount_zero_or_invalid_blocked(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(),
            fixed_amount=0.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is False
        assert result.sizing_reason == "normalized_amount_zero_or_invalid"


# ---------------------------------------------------------------------------
# TestEvaluateOrderSizeEdgeCases
# ---------------------------------------------------------------------------

class TestEvaluateOrderSizeEdgeCases:
    def test_exact_min_order_size_allowed(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=100.0,
            total_balance=100.0,
            policy=default_policy(min_order_size=10.0),
            fixed_amount=10.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is True

    def test_exact_max_order_size_allowed(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=500.0,
            total_balance=500.0,
            policy=default_policy(max_order_size=100.0),
            fixed_amount=100.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is True

    def test_exact_available_balance_allowed(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=50.0,
            total_balance=100.0,
            policy=default_policy(max_order_size=500.0),
            fixed_amount=50.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is True

    def test_exact_min_available_balance_to_trade_allowed(self):
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=5.0,
            total_balance=100.0,
            policy=default_policy(min_available_balance_to_trade=5.0),
            fixed_amount=2.0,
        )
        result = evaluate_order_size(ctx)
        assert result.size_allowed is True

    def test_disallowed_mode_checked_before_balance(self):
        """Disallowed mode must be caught before balance check."""
        ctx = SizingContext(
            sizing_mode=SizingMode.AVAILABLE_BALANCE_PERCENT,
            available_balance=0.0,  # would also fail balance check
            total_balance=0.0,
            policy=default_policy(allowed_sizing_modes=["fixed_amount"]),
            available_balance_percent=10.0,
        )
        result = evaluate_order_size(ctx)
        assert result.sizing_reason == "disallowed_sizing_mode"

    def test_min_balance_checked_before_amount_computation(self):
        """Min available balance check fires before computing amount."""
        ctx = SizingContext(
            sizing_mode=SizingMode.FIXED_AMOUNT,
            available_balance=2.0,  # below min_available_balance_to_trade=5.0
            total_balance=100.0,
            policy=default_policy(min_available_balance_to_trade=5.0),
            fixed_amount=0.0,  # would also trigger zero/invalid if reached
        )
        result = evaluate_order_size(ctx)
        assert result.sizing_reason == "below_min_available_balance_to_trade"
