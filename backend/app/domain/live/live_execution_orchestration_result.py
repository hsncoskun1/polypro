"""Live execution orchestration result — v0.7.7."""
from dataclasses import dataclass, field
from typing import List
from app.domain.live.live_execution_stage import LiveExecutionStage


@dataclass
class LiveExecutionOrchestrationResult:
    event_key: str
    current_stage: LiveExecutionStage
    orchestration_allowed: bool
    orchestration_completed: bool = False
    retryable: bool = False
    terminal_failure: bool = False
    blocker_reasons: List[str] = field(default_factory=list)
