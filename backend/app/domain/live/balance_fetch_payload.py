"""Balance fetch request payload — v1.0.2."""
from dataclasses import dataclass


@dataclass
class BalanceFetchPayload:
    """Minimal request descriptor for a balance fetch operation.

    Credentials are passed separately (LiveCredentials).
    currency is informational — Polymarket CLOB collateral is USDC.
    """
    currency: str = "USDC"
