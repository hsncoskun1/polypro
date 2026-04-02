"""Exit decision model — output from exit policy evaluation."""
from dataclasses import dataclass, field


@dataclass
class ExitDecision:
    """Output contract from exit policy evaluation.

    Fields:
        should_exit: True if any exit condition was triggered.
        exit_reason: Identifies which condition triggered the exit.
            Values: "stop_loss" | "take_profit" | "timeout" | ""
            Empty string when should_exit is False.
    """

    should_exit: bool
    exit_reason: str = field(default="")
