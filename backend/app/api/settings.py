"""GET /settings — system settings and live configuration status endpoint.

Returns SettingsResponse:
- Credential configured status (boolean only — no plaintext values)
- Live configuration state
- Trading configuration defaults
- Release gate visibility

live_applied_testing_ready is always False and never auto-enabled.
Secrets are never in the response as plaintext.
"""
from fastapi import APIRouter
from app.api.schemas.settings import SettingsResponse
from app.domain.live.client_mode import ClientMode

router = APIRouter()


def _build_settings_response() -> SettingsResponse:
    # No credentials configured in current state
    return SettingsResponse(
        # Credential configured flags — all False until user configures
        api_key_configured=False,
        api_secret_configured=False,
        api_passphrase_configured=False,
        relayer_api_configured=False,
        wallet_address_configured=False,
        funder_address_configured=False,
        private_key_configured=False,
        # Live configuration — default safe state
        explicit_live_enable=False,
        live_test_gate_enabled=False,
        live_test_gate_passed=False,
        # Trading configuration defaults
        client_mode=ClientMode.SIMULATION_MOCK.value,
        minimum_order_size=0.0,
        selected_event="",
        selected_market="",
        # Release gate
        release_ready=True,
        live_applied_testing_ready=False,  # never auto-enabled
        blocked_reason_messages=["Canlı uygulamalı test henüz yetkilendirilmedi."],
        # No credentials configured yet
        masked_secret_fields=[],
    )


@router.get("/settings", response_model=SettingsResponse)
def get_settings() -> SettingsResponse:
    """System settings and live configuration status.

    Credential values are never returned — only configured/not-configured status.
    live_applied_testing_ready is always False.
    """
    return _build_settings_response()
