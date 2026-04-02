"""Client exception type enum — v0.8.1."""
from enum import Enum


class ClientExceptionType(str, Enum):
    """Classification of exception types raised during live exchange client operations.

    Values:
        TIMEOUT: Request exceeded the configured timeout window.
        CONNECTION_ERROR: Network or transport-level connection failure.
        INVALID_RESPONSE: Exchange returned a response that cannot be parsed or validated.
        AUTH_ERROR: Authentication or authorization failure.
        RATE_LIMITED: Exchange rejected the request due to rate limiting.
        UNKNOWN: Unclassified exception — always fail-closed.
    """
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    INVALID_RESPONSE = "invalid_response"
    AUTH_ERROR = "auth_error"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"
