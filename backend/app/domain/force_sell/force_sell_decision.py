"""Force sell decision model — output from force sell evaluation."""
from dataclasses import dataclass, field


@dataclass
class ForceSellDecision:
    """Output contract from force sell evaluation.

    Fields:
        should_force_sell: True if any force sell condition was triggered.
        reason: Identifies which condition(s) triggered the force sell.

    Reason codes:
        "force_sell_time"          — time condition triggered (single-condition)
        "force_sell_pnl_loss"      — pnl-loss condition triggered (single-condition)
        "force_sell_entry_delta"   — adverse delta condition triggered (single-condition)
        "force_sell_combined_any"  — any of multiple enabled conditions fired
        "force_sell_combined_all"  — all of multiple enabled conditions fired
        ""                         — no condition triggered (should_force_sell=False)
    """

    should_force_sell: bool
    reason: str = field(default="")
