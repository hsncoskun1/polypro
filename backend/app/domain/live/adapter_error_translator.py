"""Adapter error translator — v0.8.0.

Translates external mapped_status strings and failure flags
into AdapterOutcomeStatus enum values.
Fail-closed: unknown or unrecognized status → ADAPTER_TERMINAL_FAILURE.
Unknown exchange response must never be treated as a forward-moving state.
"""
from app.domain.live.adapter_outcome_status import AdapterOutcomeStatus

_STATUS_MAP = {
    "submitted": AdapterOutcomeStatus.ADAPTER_SUBMITTED,
    "accepted": AdapterOutcomeStatus.ADAPTER_ACCEPTED,
    "rejected": AdapterOutcomeStatus.ADAPTER_REJECTED,
    "filled": AdapterOutcomeStatus.ADAPTER_ACCEPTED,
    "partially_filled": AdapterOutcomeStatus.ADAPTER_ACCEPTED,
    "cancelled": AdapterOutcomeStatus.ADAPTER_ACCEPTED,
    "replaced": AdapterOutcomeStatus.ADAPTER_ACCEPTED,
    "no_update": AdapterOutcomeStatus.ADAPTER_NO_UPDATE,
    "update_received": AdapterOutcomeStatus.ADAPTER_UPDATE_RECEIVED,
    "": AdapterOutcomeStatus.ADAPTER_SUBMITTED,
}


def translate_status(
    mapped_status: str,
    terminal_failure: bool = False,
    retryable: bool = False,
) -> AdapterOutcomeStatus:
    """Translate external status string to AdapterOutcomeStatus.

    Priority:
      1. terminal_failure=True → ADAPTER_TERMINAL_FAILURE
      2. retryable=True        → ADAPTER_RETRYABLE_FAILURE
      3. mapped_status lookup  → enum value
      4. Unknown status        → ADAPTER_TERMINAL_FAILURE (fail-closed, never forward-moving)
    """
    if terminal_failure:
        return AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE
    if retryable:
        return AdapterOutcomeStatus.ADAPTER_RETRYABLE_FAILURE
    return _STATUS_MAP.get(mapped_status, AdapterOutcomeStatus.ADAPTER_TERMINAL_FAILURE)
