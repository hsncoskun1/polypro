from fastapi import APIRouter, HTTPException, Request

from app.api.schemas.discovery import (
    DiscoverySummarySchema,
    DiscoveryTriggerRequest,
    DiscoveryTriggerResponse,
)
from app.clients.polymarket import PolymarketClient, PolymarketClientError
from app.clients.polymarket_mapping import ClientPayloadMappingError
from app.clients.timeframe_mapping import TimeframeMappingError
from app.core.config import POLYMARKET_URL
from app.services.discovery_client import run_polymarket_fetch_to_discovery

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery"])


@router.post("/trigger", response_model=DiscoveryTriggerResponse)
def trigger_discovery(body: DiscoveryTriggerRequest, request: Request) -> DiscoveryTriggerResponse:
    registry = request.app.state.market_registry
    url = body.url or POLYMARKET_URL
    client = PolymarketClient(url, timeout=body.timeout)
    try:
        result = run_polymarket_fetch_to_discovery(client, registry, source_name=body.source_name)
    except PolymarketClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except (ClientPayloadMappingError, TimeframeMappingError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
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
