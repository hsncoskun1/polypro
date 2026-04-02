"""Client wiring result — v0.7.9."""
from dataclasses import dataclass, field
from typing import List
from app.domain.live.client_mode import ClientMode


@dataclass
class ClientWiringResult:
    client_mode: ClientMode
    client_ready: bool
    real_outbound_allowed: bool
    dry_run_active: bool = False
    blocker_reasons: List[str] = field(default_factory=list)
