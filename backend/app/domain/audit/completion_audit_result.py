"""CompletionAuditResult — aggregate result of full roadmap audit."""
from dataclasses import dataclass, field
from typing import List

from app.domain.audit.audit_step_result import AuditStepResult
from app.domain.audit.gap_report import GapReport


@dataclass
class CompletionAuditResult:
    """
    Aggregate result of the full roadmap completion audit.

    completion_ready is True only when remaining_blockers is empty.
    live_applied_testing_ready is NEVER auto-set to True — it is always a
    separate explicit authorization step.
    """

    audit_steps: List[AuditStepResult] = field(default_factory=list)
    gap_reports: List[GapReport] = field(default_factory=list)
    completion_ready: bool = False
    remaining_blockers: List[str] = field(default_factory=list)
    live_applied_testing_ready: bool = False  # never auto-enabled

    @property
    def total_steps(self) -> int:
        return len(self.audit_steps)

    @property
    def fully_complete_steps(self) -> int:
        return sum(1 for s in self.audit_steps if s.fully_complete)

    @property
    def open_gaps(self) -> List[GapReport]:
        return [g for g in self.gap_reports if g.is_open]

    @property
    def blocking_gaps(self) -> List[GapReport]:
        return [g for g in self.gap_reports if g.is_blocking]

    @property
    def system_coverage_summary(self) -> str:
        total = self.total_steps
        complete = self.fully_complete_steps
        open_g = len(self.open_gaps)
        blocking = len(self.blocking_gaps)
        blockers = len(self.remaining_blockers)
        return (
            f"Steps: {complete}/{total} complete | "
            f"Open gaps: {open_g} | "
            f"Blocking gaps: {blocking} | "
            f"Remaining blockers: {blockers} | "
            f"Completion ready: {self.completion_ready} | "
            f"Live testing ready: {self.live_applied_testing_ready}"
        )
