"""ClaimStatus — claim lifecycle state enum."""
from enum import Enum


class ClaimStatus(str, Enum):
    NOT_CLAIMABLE_OUTCOME_UNKNOWN = "not_claimable_outcome_unknown"
    NOT_CLAIMABLE_RESOLUTION_PENDING = "not_claimable_resolution_pending"
    NOT_CLAIMABLE_CLAIM_UNAVAILABLE = "not_claimable_claim_unavailable"
    CLAIM_AVAILABLE = "claim_available"
    CLAIM_SUBMITTED = "claim_submitted"
    CLAIM_COMPLETED = "claim_completed"
    CLAIM_FAILED = "claim_failed"
