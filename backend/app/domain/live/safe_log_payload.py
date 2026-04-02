"""Safe log payload and redaction helper — v0.8.1.

Prevents secrets and sensitive fields from leaking into logs.
All logging of exchange payloads must pass through redact_payload()
before emission.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

_REDACTED = "[REDACTED]"

_DEFAULT_SENSITIVE_KEYS = frozenset({
    "api_key",
    "api_secret",
    "private_key",
    "passphrase",
    "secret",
    "password",
    "token",
    "authorization",
    "signature",
    "raw_payload",
})


def redact_payload(
    payload_dict: Dict[str, Any],
    sensitive_keys: frozenset = _DEFAULT_SENSITIVE_KEYS,
) -> Dict[str, Any]:
    """Return a copy of payload_dict with sensitive field values replaced by [REDACTED].

    Args:
        payload_dict: Dictionary representation of a payload to sanitize.
        sensitive_keys: Set of field names whose values must be redacted.

    Returns:
        New dict safe for logging — sensitive values masked, structure preserved.
    """
    return {
        k: (_REDACTED if k.lower() in sensitive_keys else v)
        for k, v in payload_dict.items()
    }


@dataclass
class SafeLogPayload:
    """Safe log payload model — carries only non-sensitive operational fields.

    Attributes:
        operation_type: Operation label (e.g. 'submit', 'cancel').
        order_id: Internal order identifier.
        correlation_id: Correlation identifier (safe to log).
        masked_fields: List of field names that were redacted from the original payload.
    """
    operation_type: str = ""
    order_id: str = ""
    correlation_id: str = ""
    masked_fields: List[str] = field(default_factory=list)
