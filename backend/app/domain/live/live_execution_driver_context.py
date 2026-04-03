"""Live execution driver input context — v1.0.4."""
from dataclasses import dataclass, field

from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.live_credentials import LiveCredentials


@dataclass
class LiveExecutionDriverContext:
    """Input context for a single live execution driver run.

    Carries the submit request, credentials, outbound guards,
    and polling configuration.

    outbound_allowed and preflight_passed are the two mandatory guards.
    Both must be True for any outbound action to proceed.

    max_poll_attempts controls how many fill-stream polls are made
    after a successful submit. Default 1 for foundation — increase
    for production polling loops.

    poll_delay_seconds: time between polls (0.0 in tests for instant runs).
    """
    event_key: str
    submit_request: AdapterSubmitRequest
    credentials: LiveCredentials
    outbound_allowed: bool = False
    preflight_passed: bool = False
    max_poll_attempts: int = 1
    poll_delay_seconds: float = 0.0
