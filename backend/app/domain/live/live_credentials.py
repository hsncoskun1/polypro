"""Live credential store — v0.7.1."""
from dataclasses import dataclass, field


@dataclass
class LiveCredentials:
    """All live-mode credentials in one place.

    Empty string means the credential is not configured.
    Values are never logged or exposed to frontend in plaintext.
    """
    wallet_address: str = ""
    private_key: str = ""
    funder_address: str = ""
    relayer_api: str = ""
    api_key: str = ""
    api_secret: str = ""
    api_passphrase: str = ""
