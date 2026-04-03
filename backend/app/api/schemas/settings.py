"""SettingsResponse — Pydantic schema for GET /settings.

Returns configuration status:
- Credential configured flags (never plaintext values)
- Live configuration state
- Trading configuration
- Release gate visibility
- Blocked reason messages
- Masked secret field list

Secrets are never included as plaintext.
"""
from typing import List
from pydantic import BaseModel


class SettingsResponse(BaseModel):
    # Credential configured status — boolean only, no plaintext values
    api_key_configured: bool
    api_secret_configured: bool
    api_passphrase_configured: bool
    relayer_api_configured: bool
    wallet_address_configured: bool
    funder_address_configured: bool
    private_key_configured: bool

    # Live configuration
    explicit_live_enable: bool
    live_test_gate_enabled: bool
    live_test_gate_passed: bool

    # Trading configuration
    client_mode: str
    minimum_order_size: float
    selected_event: str
    selected_market: str

    # Release gate
    release_ready: bool
    live_applied_testing_ready: bool
    blocked_reason_messages: List[str]

    # Masked secret field list — which credentials have values configured
    masked_secret_fields: List[str]
