"""AuditStepResult — per-roadmap-step audit record."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class AuditStepResult:
    """Records the audit outcome for a single roadmap step."""

    roadmap_step: str = ""
    implemented: bool = False
    verified: bool = False
    integrated: bool = False
    docs_aligned: bool = False
    gap_found: bool = False
    gap_closed: bool = False
    remaining_blockers: List[str] = field(default_factory=list)

    @property
    def fully_complete(self) -> bool:
        """True only when all checks pass and no remaining blockers."""
        return (
            self.implemented
            and self.verified
            and self.integrated
            and self.docs_aligned
            and not self.gap_found
            and len(self.remaining_blockers) == 0
        )

    @property
    def gap_open(self) -> bool:
        """True when a gap was found but not yet closed."""
        return self.gap_found and not self.gap_closed
