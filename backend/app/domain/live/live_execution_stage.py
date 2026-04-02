"""Live execution stage enum — v0.7.7."""
from enum import Enum


class LiveExecutionStage(str, Enum):
    PREFLIGHT_BLOCKED = "preflight_blocked"
    READY_TO_SUBMIT = "ready_to_submit"
    SUBMITTED = "submitted"
    RESPONSE_RECEIVED = "response_received"
    FILL_IN_PROGRESS = "fill_in_progress"
    FILLED = "filled"
    CANCEL_IN_PROGRESS = "cancel_in_progress"
    CANCELLED = "cancelled"
    REPLACE_IN_PROGRESS = "replace_in_progress"
    REPLACED = "replaced"
    RECONCILED = "reconciled"
    RETRYABLE_FAILURE = "retryable_failure"
    TERMINAL_FAILURE = "terminal_failure"
