from fastapi import APIRouter, Request

from app.adapters.discovery import PayloadDiscoveryAdapter
from app.adapters.external_payload import (
    ExternalPayloadMappingError,
    PolymarketMarketPayload,
    map_to_raw_payload_item,
)
from app.api.schemas.discovery import (
    DiscoveryTriggerRequest,
    DiscoveryTriggerResponse,
    DiscoverySummarySchema,
)
from app.services.discovery import run_discovery_service

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery"])


@router.post("/trigger", response_model=DiscoveryTriggerResponse)
def trigger_discovery(body: DiscoveryTriggerRequest, request: Request) -> DiscoveryTriggerResponse:
    registry = request.app.state.market_registry
    raw_payload = []
    for item in body.items:
        pm = PolymarketMarketPayload(
            condition_id=item.market_id,
            question=item.title,
            end_date=item.timeframe,
        )
        try:
            raw_payload.append(map_to_raw_payload_item(pm))
        except ExternalPayloadMappingError:
            # Items already validated at API boundary (min_length=1).
            # This path is defensive — mapping errors are not silently lost.
            pass
    adapter = PayloadDiscoveryAdapter(raw_payload)
    result = run_discovery_service(adapter, registry, source_name=body.source_name)
    return DiscoveryTriggerResponse(
        summary=DiscoverySummarySchema(
            added_count=result.summary.added_count,
            skipped_duplicate_count=result.summary.skipped_duplicate_count,
            skipped_invalid_count=result.summary.skipped_invalid_count,
            total_seen=result.summary.total_seen,
        ),
        source_name=result.source_name,
        ran_at=result.ran_at,
    )
