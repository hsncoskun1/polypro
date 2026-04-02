"""PnL evaluator — pure functions for unrealized and realized PnL calculation.

Design decisions:
- PnL is always fill-price based. Order submitted price is NEVER used as PnL basis.
  This is a binding project decision.
- Side-aware: YES/UP profits when price rises; NO/DOWN profits when price falls.
- compute_unrealized_pnl(): used for open positions (current price vs fill price).
- compute_realized_pnl(): used for closed positions (exit fill vs entry fill).
- All functions are pure — no side effects, no state mutation.
- Move value = price move in the profitable direction for the given side.
  A positive move value means the position is profitable.
"""


def compute_unrealized_pnl(
    entry_fill_price: float,
    current_price: float,
    filled_size: float,
    side: str,
) -> float:
    """Compute unrealized PnL for an open position.

    PnL is fill-price based. Side-aware: YES profits when price rises,
    NO profits when price falls.

    Args:
        entry_fill_price: Actual fill price at entry. Authoritative PnL basis.
        current_price: Current market price.
        filled_size: Actual filled position size.
        side: Trade direction — "YES"/"UP" or "NO"/"DOWN".

    Returns:
        Unrealized PnL. Positive = profitable, negative = loss.
    """
    if side in ("YES", "UP"):
        move = current_price - entry_fill_price
    else:  # "NO" / "DOWN"
        move = entry_fill_price - current_price
    return move * filled_size


def compute_realized_pnl(
    entry_fill_price: float,
    exit_fill_price: float,
    filled_size: float,
    side: str,
) -> float:
    """Compute realized PnL for a closed position.

    PnL is fill-price based (entry fill vs exit fill).
    Order submitted prices are never used as PnL basis.

    Args:
        entry_fill_price: Actual fill price at entry. Authoritative PnL basis.
        exit_fill_price: Actual fill price at exit.
        filled_size: Actual filled position size.
        side: Trade direction — "YES"/"UP" or "NO"/"DOWN".

    Returns:
        Realized PnL. Positive = profitable, negative = loss.
    """
    if side in ("YES", "UP"):
        move = exit_fill_price - entry_fill_price
    else:  # "NO" / "DOWN"
        move = entry_fill_price - exit_fill_price
    return move * filled_size


def compute_move_value(
    entry_fill_price: float,
    comparison_price: float,
    side: str,
) -> float:
    """Compute side-aware price move value.

    Positive = move in profitable direction, negative = adverse move.

    Args:
        entry_fill_price: Reference entry fill price.
        comparison_price: Price to compare against (current or exit).
        side: Trade direction.

    Returns:
        Move value relative to entry fill.
    """
    if side in ("YES", "UP"):
        return comparison_price - entry_fill_price
    else:
        return entry_fill_price - comparison_price
