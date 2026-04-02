"""Dry-run result model — v0.7.9.

Records what would have been sent without performing real outbound.
real_outbound_performed is always False in dry-run mode.
"""
from dataclasses import dataclass
from app.domain.live.client_mode import ClientMode


@dataclass
class DryRunResult:
    client_mode: ClientMode
    dry_run_action_recorded: bool
    real_outbound_performed: bool = False
    action_description: str = ""
