"""Client timeout policy — v0.8.1."""
from dataclasses import dataclass, field


@dataclass
class ClientTimeoutPolicy:
    """Timeout configuration for a live exchange client operation.

    Attributes:
        timeout_seconds: Maximum seconds to wait for an exchange response.
        retryable_on_timeout: Whether a timeout should be classified as retryable.
    """
    timeout_seconds: float = 30.0
    retryable_on_timeout: bool = True
