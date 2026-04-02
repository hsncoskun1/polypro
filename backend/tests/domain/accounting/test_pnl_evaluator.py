"""Tests for pnl_evaluator — compute_unrealized_pnl, compute_realized_pnl,
compute_move_value."""
from app.domain.accounting.pnl_evaluator import (
    compute_unrealized_pnl,
    compute_realized_pnl,
    compute_move_value,
)


# ---------------------------------------------------------------------------
# TestUnrealizedPnl
# ---------------------------------------------------------------------------

class TestUnrealizedPnl:
    def test_yes_price_above_fill_positive_pnl(self):
        """YES: price rose above fill → positive unrealized PnL."""
        result = compute_unrealized_pnl(
            entry_fill_price=0.50,
            current_price=0.60,
            filled_size=10.0,
            side="YES",
        )
        assert result == pytest.approx(1.0)

    def test_yes_price_below_fill_negative_pnl(self):
        """YES: price fell below fill → negative unrealized PnL."""
        result = compute_unrealized_pnl(
            entry_fill_price=0.60,
            current_price=0.50,
            filled_size=10.0,
            side="YES",
        )
        assert result == pytest.approx(-1.0)

    def test_no_price_below_fill_positive_pnl(self):
        """NO: price fell below fill → positive unrealized PnL."""
        result = compute_unrealized_pnl(
            entry_fill_price=0.60,
            current_price=0.50,
            filled_size=10.0,
            side="NO",
        )
        assert result == pytest.approx(1.0)

    def test_no_price_above_fill_negative_pnl(self):
        """NO: price rose above fill → negative unrealized PnL."""
        result = compute_unrealized_pnl(
            entry_fill_price=0.50,
            current_price=0.60,
            filled_size=10.0,
            side="NO",
        )
        assert result == pytest.approx(-1.0)

    def test_zero_pnl_when_price_unchanged(self):
        """Price equals fill → zero unrealized PnL."""
        result = compute_unrealized_pnl(0.50, 0.50, 10.0, "YES")
        assert result == pytest.approx(0.0)

    def test_fill_price_is_basis_not_submitted_price(self):
        """Unrealized PnL uses fill_price, not order_submitted_price."""
        # If submitted = 0.55 but fill = 0.50, PnL basis is 0.50
        fill = 0.50
        current = 0.60
        size = 10.0
        result = compute_unrealized_pnl(fill, current, size, "YES")
        assert result == pytest.approx(1.0)  # (0.60-0.50)*10


# ---------------------------------------------------------------------------
# TestRealizedPnl
# ---------------------------------------------------------------------------

class TestRealizedPnl:
    def test_yes_exit_above_entry_fill_profit(self):
        """YES: exit fill above entry fill → profit."""
        result = compute_realized_pnl(
            entry_fill_price=0.50,
            exit_fill_price=0.70,
            filled_size=10.0,
            side="YES",
        )
        assert result == pytest.approx(2.0)

    def test_yes_exit_below_entry_fill_loss(self):
        """YES: exit fill below entry fill → loss."""
        result = compute_realized_pnl(
            entry_fill_price=0.60,
            exit_fill_price=0.45,
            filled_size=10.0,
            side="YES",
        )
        assert result == pytest.approx(-1.5)

    def test_no_exit_below_entry_fill_profit(self):
        """NO: exit fill below entry fill → profit."""
        result = compute_realized_pnl(
            entry_fill_price=0.60,
            exit_fill_price=0.40,
            filled_size=10.0,
            side="NO",
        )
        assert result == pytest.approx(2.0)

    def test_no_exit_above_entry_fill_loss(self):
        """NO: exit fill above entry fill → loss."""
        result = compute_realized_pnl(
            entry_fill_price=0.40,
            exit_fill_price=0.60,
            filled_size=10.0,
            side="NO",
        )
        assert result == pytest.approx(-2.0)

    def test_realized_pnl_fill_price_based_not_submitted(self):
        """Realized PnL uses fill prices, not order_submitted_price."""
        # submitted might be 0.55 but fill is 0.50; PnL basis is fill
        result = compute_realized_pnl(
            entry_fill_price=0.50,
            exit_fill_price=0.70,
            filled_size=5.0,
            side="YES",
        )
        assert result == pytest.approx(1.0)  # (0.70-0.50)*5

    def test_zero_realized_pnl_when_exit_equals_entry_fill(self):
        """Exit at same price as entry fill → zero realized PnL."""
        result = compute_realized_pnl(0.50, 0.50, 10.0, "YES")
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# TestMoveValue
# ---------------------------------------------------------------------------

class TestMoveValue:
    def test_yes_positive_move(self):
        result = compute_move_value(0.50, 0.60, "YES")
        assert result == pytest.approx(0.10)

    def test_no_positive_move(self):
        result = compute_move_value(0.60, 0.50, "NO")
        assert result == pytest.approx(0.10)

    def test_adverse_move_is_negative(self):
        result = compute_move_value(0.60, 0.50, "YES")
        assert result == pytest.approx(-0.10)


import pytest
