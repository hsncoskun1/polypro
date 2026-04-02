"""Live execution preflight evaluation input contract — v0.7.2."""
from dataclasses import dataclass
from app.domain.live.outbound_action_type import OutboundActionType


@dataclass
class PreflightContext:
    # Mode state
    simulation_mode_default: bool
    live_mode_requested: bool
    live_mode_enabled: bool
    explicit_live_enable: bool

    # Upstream gate results
    credentials_complete: bool
    verification_passed: bool
    sizing_passed: bool
    risk_passed: bool

    # The outbound action being guarded
    outbound_action_type: OutboundActionType
