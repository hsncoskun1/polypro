"""Credential completeness evaluator — v0.7.1.

All field checks run — no short-circuit.
Produces masked_summary for safe visibility (no plaintext secrets).
"""
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.secrets_masker import mask_secret
from app.domain.live.secrets_result import SecretsResult

_CREDENTIAL_FIELDS = [
    "wallet_address",
    "private_key",
    "funder_address",
    "relayer_api",
    "api_key",
    "api_secret",
    "api_passphrase",
]


def evaluate_credential_completeness(creds: LiveCredentials) -> SecretsResult:
    """Check all credential fields and return completeness result.

    All checks run — no short-circuit.
    masked_summary contains masked values for every field (safe for logging/display).
    """
    missing = []
    masked = {}

    for field_name in _CREDENTIAL_FIELDS:
        value = getattr(creds, field_name)
        masked[field_name] = mask_secret(value)
        if not value:
            missing.append(field_name)

    return SecretsResult(
        is_complete=len(missing) == 0,
        missing_fields=missing,
        masked_summary=masked,
    )
