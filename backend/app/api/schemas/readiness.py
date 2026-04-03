"""Readiness API schema — v0.8.7."""
from typing import List, Optional
from pydantic import BaseModel


class ReadinessResponse(BaseModel):
    launcher_blocked: bool
    setup_completed: bool
    update_required: bool
    preflight_passed: bool
    backend_ready: bool
    final_backend_ready: bool
    release_ready: bool
    live_applied_testing_ready: bool
    blocked_reason_messages: List[str]
    continue_destination: Optional[str]
    frontend_port: int
    backend_port: int
    readiness_poll_interval_ms: int
