"""Live order cancel status enum — v0.7.5."""
from enum import Enum


class CancelStatus(str, Enum):
    CANCEL_ALLOWED_NOT_ATTEMPTED = "cancel_allowed_not_attempted"
    CANCEL_BLOCKED_PREFLIGHT = "cancel_blocked_preflight"
    CANCEL_BLOCKED_OUTBOUND_GUARD = "cancel_blocked_outbound_guard"
    CANCEL_READY = "cancel_ready"
    CANCEL_SUBMITTED = "cancel_submitted"
    CANCEL_REJECTED = "cancel_rejected"
    CANCEL_RETRYABLE_FAILURE = "cancel_retryable_failure"
    CANCEL_TERMINAL_FAILURE = "cancel_terminal_failure"
