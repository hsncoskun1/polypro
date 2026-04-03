"""Live credential store — v1.0.8."""
from dataclasses import dataclass


@dataclass
class LiveCredentials:
    """All live-mode credentials in one place.

    Empty string means the credential is not configured.
    Values are never logged or exposed to frontend in plaintext.

    __repr__ and __str__ are overridden to prevent accidental credential
    exposure in logs, tracebacks, or debug output.
    """
    wallet_address: str = ""
    private_key: str = ""
    funder_address: str = ""
    relayer_api: str = ""
    api_key: str = ""
    api_secret: str = ""
    api_passphrase: str = ""

    def __repr__(self) -> str:
        configured = [
            f for f in ("wallet_address", "private_key", "funder_address",
                        "relayer_api", "api_key", "api_secret", "api_passphrase")
            if getattr(self, f)
        ]
        return f"LiveCredentials(configured={configured}, values=[REDACTED])"

    def __str__(self) -> str:
        return self.__repr__()
