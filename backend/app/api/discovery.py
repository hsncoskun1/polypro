from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.deps import verify_trigger_auth
from app.api.schemas.discovery import (
    DiscoverySummarySchema,
    DiscoveryRunStatusResponse,
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
def trigger_discovery(
    body: DiscoveryTriggerRequest,
    request: Request,
    _: None = Depends(verify_trigger_auth),
) -> DiscoveryTriggerResponse:
    guard = request.app.state.discovery_run_guard
    status = request.app.state.discovery_run_status
    if not guard.acquire():
        raise HTTPException(status_code=409, detail="Discovery run already in progress")
    status.is_running = True
    status.last_error = None
    try:
        registry = request.app.state.market_registry
        url = body.url or POLYMARKET_URL
        client = PolymarketClient(url, timeout=body.timeout)
        try:
            result = run_polymarket_fetch_to_discovery(client, registry, source_name=body.source_name)
        except PolymarketClientError as exc:
            raise HTTPException(status_code=502, detail=str(exc))
        except (ClientPayloadMappingError, TimeframeMappingError) as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        now = datetime.now(tz=timezone.utc)
        status.last_finished_at = now
        status.last_success_at = now
        status.last_result_summary = {
            "added_count": result.summary.added_count,
            "skipped_duplicate_count": result.summary.skipped_duplicate_count,
            "skipped_invalid_count": result.summary.skipped_invalid_count,
            "total_seen": result.summary.total_seen,
        }
    except HTTPException as exc:
        status.last_finished_at = datetime.now(tz=timezone.utc)
        status.last_error = exc.detail
        raise
    finally:
        status.is_running = False
        guard.release()
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


@router.get("/status", response_model=DiscoveryRunStatusResponse)
def get_discovery_status(
    request: Request,
    _: None = Depends(verify_trigger_auth),
) -> DiscoveryRunStatusResponse:
    status = request.app.state.discovery_run_status
    return DiscoveryRunStatusResponse(
        is_running=status.is_running,
        last_finished_at=status.last_finished_at,
        last_success_at=status.last_success_at,
        last_result_summary=status.last_result_summary,
        last_error=status.last_error,
    )
