from fastapi import APIRouter, Request

from app.adapters.discovery import PayloadDiscoveryAdapter, RawPayloadItem
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
    raw_payload = [
        RawPayloadItem(
            market_id=item.market_id,
            title=item.title,
            timeframe=item.timeframe,
        )
        for item in body.items
    ]
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
