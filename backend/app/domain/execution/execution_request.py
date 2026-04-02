"""Execution request model — input to simulation execution."""
from dataclasses import dataclass


@dataclass
class ExecutionRequest:
    """Input contract for simulation entry and exit operations.

    Fields:
        event_key: Unique identifier for the market event being traded.
        side: Trade direction — "YES" or "NO".
        requested_size: Position size requested by the strategy.
        simulated_fill_price: Price at which the paper trade is filled.
    """

    event_key: str
    side: str
    requested_size: float
    simulated_fill_price: float
