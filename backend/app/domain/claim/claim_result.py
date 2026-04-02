"""ClaimResult — output of claim/settlement state evaluation."""
from dataclasses import dataclass
from typing import Optional
from app.domain.claim.claim_status import ClaimStatus


@dataclass
class ClaimResult:
    claim_status: ClaimStatus
    is_claimable: bool
    balance_after_claim: float
    claimed_amount: float
    claim_adjusted_balance_effect: float
    early_exit_realized_pnl: float
    settlement_effect: float
    settlement_completed_at: Optional[str]
