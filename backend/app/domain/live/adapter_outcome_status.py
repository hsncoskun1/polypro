"""Adapter outcome status enum — v0.7.8."""
from enum import Enum


class AdapterOutcomeStatus(str, Enum):
    ADAPTER_SUBMITTED = "adapter_submitted"
    ADAPTER_ACCEPTED = "adapter_accepted"
    ADAPTER_REJECTED = "adapter_rejected"
    ADAPTER_RETRYABLE_FAILURE = "adapter_retryable_failure"
    ADAPTER_TERMINAL_FAILURE = "adapter_terminal_failure"
    ADAPTER_UPDATE_RECEIVED = "adapter_update_received"
    ADAPTER_NO_UPDATE = "adapter_no_update"
