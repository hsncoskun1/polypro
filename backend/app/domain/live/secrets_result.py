"""Credential completeness evaluation result — v0.7.1."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SecretsResult:
    is_complete: bool
    missing_fields: List[str] = field(default_factory=list)
    masked_summary: Dict[str, str] = field(default_factory=dict)
