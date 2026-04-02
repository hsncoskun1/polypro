"""Live order replace status enum — v0.7.5."""
from enum import Enum


class ReplaceStatus(str, Enum):
    REPLACE_ALLOWED_NOT_ATTEMPTED = "replace_allowed_not_attempted"
    REPLACE_BLOCKED_PREFLIGHT = "replace_blocked_preflight"
    REPLACE_BLOCKED_OUTBOUND_GUARD = "replace_blocked_outbound_guard"
    REPLACE_READY = "replace_ready"
    REPLACE_SUBMITTED = "replace_submitted"
    REPLACE_REJECTED = "replace_rejected"
    REPLACE_RETRYABLE_FAILURE = "replace_retryable_failure"
    REPLACE_TERMINAL_FAILURE = "replace_terminal_failure"
