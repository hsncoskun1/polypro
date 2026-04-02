"""Adapter factory / provider resolver — v0.7.9.

resolve_adapter(): Returns the appropriate LiveExchangeClient for the given
client mode. No production client is implemented yet — LIVE_PRODUCTION
requires a production_client argument.

SIMULATION_MOCK / LIVE_MOCK / LIVE_DRY_RUN → mock adapter (no real outbound)
LIVE_PRODUCTION                             → production_client (required)
"""
from typing import Optional
from app.domain.live.client_mode import ClientMode
from app.domain.live.client_wiring_context import ClientWiringContext
from app.domain.live.live_exchange_client import LiveExchangeClient
from app.domain.live.mock_live_exchange_client import MockLiveExchangeClient


def resolve_adapter(
    ctx: ClientWiringContext,
    mock_client: Optional[LiveExchangeClient] = None,
    production_client: Optional[LiveExchangeClient] = None,
) -> LiveExchangeClient:
    """Resolve the correct adapter for the given client wiring context.

    Args:
        ctx: Client wiring context with mode and readiness flags.
        mock_client: Optional pre-configured mock client. If None, a default
            MockLiveExchangeClient is used for non-production modes.
        production_client: Required for LIVE_PRODUCTION mode.

    Returns:
        LiveExchangeClient instance appropriate for the client mode.

    Raises:
        ValueError: If LIVE_PRODUCTION mode is requested but no production_client provided.
    """
    if ctx.client_mode in (
        ClientMode.SIMULATION_MOCK,
        ClientMode.LIVE_MOCK,
        ClientMode.LIVE_DRY_RUN,
    ):
        return mock_client if mock_client is not None else MockLiveExchangeClient()

    if ctx.client_mode == ClientMode.LIVE_PRODUCTION:
        if production_client is None:
            raise ValueError(
                "production_client is required for LIVE_PRODUCTION mode. "
                "No production exchange client is implemented yet."
            )
        return production_client

    raise ValueError(f"Unknown client mode: {ctx.client_mode}")
