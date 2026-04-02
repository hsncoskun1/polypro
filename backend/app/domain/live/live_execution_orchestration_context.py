"""Live execution orchestration context — v0.7.7.

Carries the known status from all sub-layer seams into the orchestrator.
Status fields use string values matching the respective sub-layer enum values.
"""
from dataclasses import dataclass


@dataclass
class LiveExecutionOrchestrationContext:
    event_key: str
    order_id: str = ""
    live_mode_requested: bool = False
    outbound_allowed: bool = False
    preflight_passed: bool = False
    submission_status: str = ""
    response_status: str = ""
    fill_confirmation_status: str = ""
    cancel_status: str = ""
    replace_status: str = ""
    reconciliation_status: str = ""
    terminal_failure: bool = False
    retryable: bool = False
