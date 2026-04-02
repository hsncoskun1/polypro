"""Client retry policy — v0.8.1."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ClientRetryPolicy:
    """Retry configuration for a live exchange client operation.

    Attributes:
        max_retries: Maximum number of retry attempts.
        retry_delay_seconds: Delay between retry attempts in seconds.
        retryable_error_codes: Error codes that are eligible for retry.
    """
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    retryable_error_codes: List[str] = field(default_factory=list)
