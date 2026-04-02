"""Client wiring context — v0.7.9.

Carries configuration state for client mode selection and production readiness.
"""
from dataclasses import dataclass
from app.domain.live.client_mode import ClientMode


@dataclass
class ClientWiringContext:
    client_mode: ClientMode
    simulation_mode: bool = True
    live_mode_requested: bool = False
    production_client_selected: bool = False
    mock_client_selected: bool = False
    dry_run_enabled: bool = False
    outbound_execution_enabled: bool = False
    production_wiring_ready: bool = False
