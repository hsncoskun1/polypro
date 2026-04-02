"""Live order submission status enum — v0.7.3."""
from enum import Enum


class OrderSubmissionStatus(str, Enum):
    SUBMISSION_ALLOWED_NOT_ATTEMPTED = "submission_allowed_not_attempted"
    SUBMISSION_BLOCKED_PREFLIGHT = "submission_blocked_preflight"
    SUBMISSION_BLOCKED_OUTBOUND_GUARD = "submission_blocked_outbound_guard"
    SUBMISSION_READY = "submission_ready"
    SUBMISSION_SUBMITTED = "submission_submitted"
    SUBMISSION_REJECTED = "submission_rejected"
    SUBMISSION_RETRYABLE_FAILURE = "submission_retryable_failure"
    SUBMISSION_TERMINAL_FAILURE = "submission_terminal_failure"
