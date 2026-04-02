"""GapReport — describes a single discovered gap."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class GapReport:
    """Describes a single technical, integration, or docs gap."""

    gap_type: str = ""          # e.g. "integration_seam", "docs_misalignment", "state_divergence"
    description: str = ""
    severity: str = "low"       # "low" | "medium" | "high"
    affected_steps: List[str] = field(default_factory=list)
    closed: bool = False
    closure_note: str = ""

    @property
    def is_open(self) -> bool:
        return not self.closed

    @property
    def is_blocking(self) -> bool:
        return self.is_open and self.severity == "high"
