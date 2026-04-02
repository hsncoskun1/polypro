"""Force sell context model — input to force sell evaluation."""
from dataclasses import dataclass


@dataclass
class ForceSellContext:
    """Input contract for force sell evaluation.

    Force sell decisions are entry/fill-based, not PTB-based.
    Three independent conditions can be enabled independently:
    time, pnl-loss, and entry/fill adverse delta.

    Fields:
        time_remaining: Time remaining before market resolution.
        force_sell_time_enabled: Whether the time condition is active.
        force_sell_time_seconds: Time threshold — triggers when time_remaining <= this.
        force_sell_pnl_loss_enabled: Whether the pnl-loss condition is active.
        force_sell_entry_delta_enabled: Whether the adverse delta condition is active.
        force_sell_entry_delta_threshold: Adverse move threshold for entry delta rule.
        force_sell_logic: Combinator for multi-condition evaluation. "any" or "all".
        entry_fill_price: Price at which the position was entered/filled.
        current_price: Current market price.
        current_pnl: Current profit/loss of the position (negative = loss).
        side: Trade direction — "YES" or "NO".
    """

    time_remaining: float
    force_sell_time_enabled: bool
    force_sell_time_seconds: float
    force_sell_pnl_loss_enabled: bool
    force_sell_entry_delta_enabled: bool
    force_sell_entry_delta_threshold: float
    force_sell_logic: str  # "any" | "all"
    entry_fill_price: float
    current_price: float
    current_pnl: float
    side: str  # "YES" | "NO"
