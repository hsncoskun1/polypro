"""Execution result model — output from simulation execution."""
from dataclasses import dataclass, field


@dataclass
class ExecutionResult:
    """Output contract from simulation entry and exit operations.

    Fields:
        success: True if execution completed successfully.
        order_id: Paper order identifier. Empty string on failure.
        fill_price: Price at which the paper trade was filled. 0.0 on failure.
        side: Trade direction reflected from the request.
        size: Position size filled. 0.0 on failure.
        reason: Empty on success. Contains failure reason identifier on failure.
    """

    success: bool
    order_id: str
    fill_price: float
    side: str
    size: float
    reason: str = field(default="")
