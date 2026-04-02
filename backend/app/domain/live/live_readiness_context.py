"""Live readiness evaluation input contract — v0.7.0."""
from dataclasses import dataclass


@dataclass
class LiveReadinessContext:
    # Mode intent
    simulation_mode_default: bool
    live_mode_requested: bool
    live_mode_enabled: bool
    explicit_live_enable: bool

    # Wallet / chain credentials
    wallet_address_present: bool
    private_key_present: bool
    funder_address_present: bool
    relayer_api_present: bool

    # Exchange API credentials
    api_key_present: bool
    api_secret_present: bool
    api_passphrase_present: bool
