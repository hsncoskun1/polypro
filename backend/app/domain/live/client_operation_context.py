"""Client operation context — v0.8.1."""
from dataclasses import dataclass, field


@dataclass
class ClientOperationContext:
    """Context carried through a single live exchange client operation.

    Holds correlation/idempotency identifiers and timeout configuration
    so they can be forwarded across the request lifecycle without being
    embedded in the adapter request/response payloads.

    Attributes:
        operation_type: String label for the operation (e.g. 'submit', 'cancel', 'replace').
        order_id: Internal order identifier.
        correlation_id: External correlation identifier for tracing across systems.
        idempotency_key: Key used to deduplicate repeated requests at the exchange.
        timeout_seconds: Per-operation timeout override.
    """
    operation_type: str
    order_id: str
    correlation_id: str = ""
    idempotency_key: str = ""
    timeout_seconds: float = 30.0
