"""Normalized client exception model — v0.8.1."""
from dataclasses import dataclass, field
from app.domain.live.client_exception_type import ClientExceptionType


@dataclass
class NormalizedClientException:
    """Normalized representation of an exception raised during a live exchange operation.

    All exchange-facing errors are translated into this model before propagating
    to the adapter layer. Unknown or unclassified errors are always terminal (fail-closed).

    Attributes:
        exception_type: Classification of the exception.
        normalized_error_code: Stable error code string (e.g. 'client_timeout').
        normalized_error_message: Human-readable normalized description.
        retryable: Whether this exception permits a retry attempt.
        terminal_failure: Whether this exception must terminate the operation.
        raw_error_type: Original exception class name or raw type string for traceability.
    """
    exception_type: ClientExceptionType = ClientExceptionType.UNKNOWN
    normalized_error_code: str = ""
    normalized_error_message: str = ""
    retryable: bool = False
    terminal_failure: bool = True
    raw_error_type: str = ""
