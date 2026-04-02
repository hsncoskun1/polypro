"""Tests for exit_fill_accounting — compute_exit_fill_accounting()."""
import pytest
from app.domain.accounting.accounting_context import AccountingContext
from app.domain.accounting.exit_fill_accounting import compute_exit_fill_accounting


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ctx(
    side="YES",
    entry_trigger_price=0.48,
    entry_order_submitted_price=0.49,
    entry_fill_price=0.50,
    exit_trigger_price=0.68,
    exit_order_submitted_price=0.69,
    exit_fill_price=0.70,
    current_price=0.70,
    requested_size=10.0,
    filled_size=10.0,
    total_balance=1000.0,
    available_balance=900.0,
    session_start_balance=1000.0,
    prior_session_realized_pnl=0.0,
    claim_adjusted_balance_effect=0.0,
):
    return AccountingContext(
        side=side,
        entry_trigger_price=entry_trigger_price,
        entry_order_submitted_price=entry_order_submitted_price,
        entry_fill_price=entry_fill_price,
        exit_trigger_price=exit_trigger_price,
        exit_order_submitted_price=exit_order_submitted_price,
        exit_fill_price=exit_fill_price,
        current_price=current_price,
        requested_size=requested_size,
        filled_size=filled_size,
        total_balance=total_balance,
        available_balance=available_balance,
        session_start_balance=session_start_balance,
        prior_session_realized_pnl=prior_session_realized_pnl,
        claim_adjusted_balance_effect=claim_adjusted_balance_effect,
    )


# ---------------------------------------------------------------------------
# TestExitFillAccountingSnapshot
# ---------------------------------------------------------------------------

class TestExitFillAccountingSnapshot:
    def test_exit_fill_accounting_snapshot_correct(self):
        """Exit fill accounting produces correct snapshot for YES position."""
        ctx = _ctx(entry_fill_price=0.50, exit_fill_price=0.70, filled_size=10.0)
        snap = compute_exit_fill_accounting(ctx)
        assert snap.exit_fill_price == 0.70
        assert snap.entry_fill_price == 0.50
        assert snap.realized_pnl == pytest.approx(2.0)

    def test_realized_pnl_fill_price_based(self):
        """Realized PnL uses fill prices, not submitted prices."""
        # entry_submitted=0.49 but fill=0.50; exit_submitted=0.69 but fill=0.70
        # PnL = (0.70-0.50)*10 = 2.0, NOT (0.69-0.49)*10=2.0 coincidentally
        # Use different values to verify
        ctx = _ctx(
            entry_order_submitted_price=0.55,  # different from fill
            entry_fill_price=0.50,
            exit_order_submitted_price=0.65,   # different from fill
            exit_fill_price=0.70,
            filled_size=10.0,
            side="YES",
        )
        snap = compute_exit_fill_accounting(ctx)
        # PnL must be (0.70-0.50)*10=2.0, NOT based on submitted prices
        assert snap.realized_pnl == pytest.approx(2.0)

    def test_unrealized_pnl_is_zero_after_exit(self):
        """Position closed — unrealized PnL must be 0.0."""
        snap = compute_exit_fill_accounting(_ctx())
        assert snap.unrealized_pnl == pytest.approx(0.0)

    def test_exit_prices_populated(self):
        """Exit trigger, submitted, fill prices all stored."""
        ctx = _ctx(
            exit_trigger_price=0.68,
            exit_order_submitted_price=0.69,
            exit_fill_price=0.70,
        )
        snap = compute_exit_fill_accounting(ctx)
        assert snap.exit_trigger_price == 0.68
        assert snap.exit_order_submitted_price == 0.69
        assert snap.exit_fill_price == 0.70

    def test_session_realized_pnl_accumulates(self):
        """session_realized_pnl = prior_realized + this position's realized."""
        ctx = _ctx(
            entry_fill_price=0.50,
            exit_fill_price=0.70,
            filled_size=10.0,
            session_start_balance=1000.0,
            prior_session_realized_pnl=3.0,  # prior trades
        )
        snap = compute_exit_fill_accounting(ctx)
        assert snap.realized_pnl == pytest.approx(2.0)
        assert snap.session_realized_pnl == pytest.approx(5.0)  # 3.0 + 2.0
        assert snap.current_balance == pytest.approx(1005.0)

    def test_current_balance_excludes_unrealized(self):
        """current_balance = session_start + session_realized (not unrealized)."""
        ctx = _ctx(
            entry_fill_price=0.50,
            exit_fill_price=0.60,
            filled_size=10.0,
            session_start_balance=1000.0,
        )
        snap = compute_exit_fill_accounting(ctx)
        realized = (0.60 - 0.50) * 10  # = 1.0
        assert snap.current_balance == pytest.approx(1000.0 + realized)

    def test_no_side_realized_pnl(self):
        """NO position: exit below entry fill → profit."""
        ctx = _ctx(
            side="NO",
            entry_fill_price=0.60,
            exit_fill_price=0.40,
            filled_size=10.0,
        )
        snap = compute_exit_fill_accounting(ctx)
        assert snap.realized_pnl == pytest.approx(2.0)

    def test_yes_loss_scenario(self):
        """YES: exit below entry fill → loss."""
        ctx = _ctx(
            side="YES",
            entry_fill_price=0.60,
            exit_fill_price=0.45,
            filled_size=10.0,
        )
        snap = compute_exit_fill_accounting(ctx)
        assert snap.realized_pnl == pytest.approx(-1.5)

    def test_session_unrealized_pnl_is_zero_after_exit(self):
        """After position closed, session_unrealized_pnl = 0.0."""
        snap = compute_exit_fill_accounting(_ctx())
        assert snap.session_unrealized_pnl == pytest.approx(0.0)

    def test_total_and_available_balance_carried(self):
        """total_balance and available_balance carried from context."""
        ctx = _ctx(total_balance=5000.0, available_balance=4500.0)
        snap = compute_exit_fill_accounting(ctx)
        assert snap.total_balance == 5000.0
        assert snap.available_balance == 4500.0
