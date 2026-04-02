"""Credential → readiness flags bridge — v0.7.1.

Converts LiveCredentials into the presence-flag dict
that feeds LiveReadinessContext credential fields.
No logic duplication — single source of truth.
"""
from typing import Dict
from app.domain.live.live_credentials import LiveCredentials


def credentials_to_readiness_flags(creds: LiveCredentials) -> Dict[str, bool]:
    """Return presence-flag dict derived from LiveCredentials.

    Each flag is True only when the corresponding credential is non-empty.
    Result maps directly onto LiveReadinessContext credential fields.
    """
    return {
        "wallet_address_present": bool(creds.wallet_address),
        "private_key_present": bool(creds.private_key),
        "funder_address_present": bool(creds.funder_address),
        "relayer_api_present": bool(creds.relayer_api),
        "api_key_present": bool(creds.api_key),
        "api_secret_present": bool(creds.api_secret),
        "api_passphrase_present": bool(creds.api_passphrase),
    }
