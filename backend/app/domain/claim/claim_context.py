"""ClaimContext — input contract for claim/settlement evaluation."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClaimContext:
    # Claim gate fields — must all be True before a claim is possible
    event_outcome_known: bool
    resolution_finalized: bool
    claim_available: bool

    # Claim lifecycle state (set externally by relayer/tracker)
    claim_submitted: bool = False
    claim_completed: bool = False
    claim_failed: bool = False

    # Settlement amounts
    claimed_amount: float = 0.0
    settlement_completed_at: Optional[str] = None

    # Balance basis for post-claim reconciliation
    balance_before_claim: float = 0.0

    # PnL separation — early exit pnl and settlement effect are never mixed
    early_exit_realized_pnl: float = 0.0
    settlement_effect: float = 0.0

    # Seam field — claim_adjusted_balance_effect is not computed here;
    # it is carried from upstream accounting and applied post-claim
    claim_adjusted_balance_effect: float = 0.0
