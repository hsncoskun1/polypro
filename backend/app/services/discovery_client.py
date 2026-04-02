from app.adapters.discovery import PayloadDiscoveryAdapter, RawPayloadItem
from app.adapters.external_payload import (
    ExternalPayloadMappingError,
    PolymarketMarketPayload,
    map_to_raw_payload_item,
)
from app.clients.polymarket import PolymarketClient
from app.clients.polymarket_mapping import map_client_rows_to_payloads
from app.clients.timeframe_mapping import map_end_date_to_timeframe
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
        → map_end_date_to_timeframe()       [ISO date → Timeframe enum]
        → map_to_raw_payload_item()
        → PayloadDiscoveryAdapter
        → run_discovery_service()

    TimeframeMappingError (past date or unparseable end_date) propagates openly.
    ExternalPayloadMappingError (empty field) is caught defensively.
    No silent fallback.
    Not wired to the trigger endpoint — integration shell only.
    """
    client = PolymarketClient(url, timeout=timeout)
    rows = client.fetch()

    pm_payloads = map_client_rows_to_payloads(rows)

    raw_items: list[RawPayloadItem] = []
    for pm in pm_payloads:
        timeframe = map_end_date_to_timeframe(pm.end_date)  # raises TimeframeMappingError if bad
        pm_mapped = PolymarketMarketPayload(
            condition_id=pm.condition_id,
            question=pm.question,
            end_date=timeframe.value,
        )
        try:
            raw_items.append(map_to_raw_payload_item(pm_mapped))
        except ExternalPayloadMappingError:
            # Whitespace-only fields that slipped through mapping layer.
            # ExternalPayloadMappingError here means an empty field — defensive catch.
            pass

    adapter = PayloadDiscoveryAdapter(raw_items)
    return run_discovery_service(adapter, registry, source_name=source_name)
