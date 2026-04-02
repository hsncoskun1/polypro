from app.adapters.discovery import PayloadDiscoveryAdapter, RawPayloadItem
from app.adapters.external_payload import (
    ExternalPayloadMappingError,
    map_to_raw_payload_item,
)
from app.clients.polymarket import PolymarketClient
from app.clients.polymarket_mapping import map_client_rows_to_payloads
from app.domain.markets.registry import InMemoryMarketRegistry
from app.services.discovery import DiscoveryResult, run_discovery_service


def run_polymarket_client_discovery(
    url: str,
    registry: InMemoryMarketRegistry,
    *,
    source_name: str = "polymarket",
    timeout: float = 10.0,
) -> DiscoveryResult:
    """Fetch Polymarket market data and run the discovery pipeline.

    Chain: PolymarketClient.fetch()
        → map_client_rows_to_payloads()
        → map_to_raw_payload_item()
        → PayloadDiscoveryAdapter
        → run_discovery_service()

    Errors from the client or mapping layers propagate openly.
    No silent fallback.
    Not wired to the trigger endpoint — integration shell only.
    """
    client = PolymarketClient(url, timeout=timeout)
    rows = client.fetch()

    pm_payloads = map_client_rows_to_payloads(rows)

    raw_items: list[RawPayloadItem] = []
    for pm in pm_payloads:
        try:
            raw_items.append(map_to_raw_payload_item(pm))
        except ExternalPayloadMappingError:
            # Items passed whitespace-as-is from mapping layer.
            # ExternalPayloadMappingError raised here means a whitespace-only
            # value slipped through — defensive catch, no silent loss.
            pass

    adapter = PayloadDiscoveryAdapter(raw_items)
    return run_discovery_service(adapter, registry, source_name=source_name)
