"""Exit context model — input to exit policy evaluation."""
from dataclasses import dataclass


@dataclass
class ExitContext:
    """Input contract for exit policy evaluation.

    Fields:
        entry_price: Price at which the position was entered.
        current_price: Current market price for the position.
        side: Trade direction — "YES" or "NO".
        stop_loss_threshold: Absolute price move that triggers a stop loss exit.
        take_profit_threshold: Absolute price move that triggers a take profit exit.
        time_remaining: Time remaining before market resolution (seconds or similar).
            A value of 0 or below indicates timeout/resolution is imminent.
    """

    entry_price: float
    current_price: float
    side: str
    stop_loss_threshold: float
    take_profit_threshold: float
    time_remaining: float
