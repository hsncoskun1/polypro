from fastapi import APIRouter, HTTPException, Request
from app.api.schemas.markets import MarketCreate, MarketResponse, StatusUpdate
from app.domain.markets.model import Market
from app.domain.markets.registry import parse_timeframe
from app.domain.markets.exceptions import (
    DuplicateMarketError,
    MarketNotFoundError,
    InvalidTimeframeError,
)

router = APIRouter(prefix="/api/v1/markets", tags=["markets"])


def _to_response(market: Market) -> MarketResponse:
    return MarketResponse(
        market_id=market.market_id,
        title=market.title,
        timeframe=market.timeframe,
        status=market.status,
    )


@router.get("", response_model=list[MarketResponse])
def list_markets(request: Request) -> list[MarketResponse]:
    registry = request.app.state.market_registry
    return [_to_response(m) for m in registry.list()]


@router.get("/active", response_model=list[MarketResponse])
def list_active_markets(request: Request) -> list[MarketResponse]:
    registry = request.app.state.market_registry
    return [_to_response(m) for m in registry.list(active_only=True)]


@router.get("/{market_id}", response_model=MarketResponse)
def get_market(market_id: str, request: Request) -> MarketResponse:
    registry = request.app.state.market_registry
    try:
        return _to_response(registry.get(market_id))
    except MarketNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("", response_model=MarketResponse, status_code=201)
def create_market(body: MarketCreate, request: Request) -> MarketResponse:
    registry = request.app.state.market_registry
    try:
        timeframe = parse_timeframe(body.timeframe)
    except InvalidTimeframeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    market = Market(market_id=body.market_id, title=body.title, timeframe=timeframe)
    try:
        registry.add(market)
    except DuplicateMarketError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _to_response(market)


@router.patch("/{market_id}/status", response_model=MarketResponse)
def update_market_status(
    market_id: str, body: StatusUpdate, request: Request
) -> MarketResponse:
    registry = request.app.state.market_registry
    try:
        registry.update_status(market_id, body.status)
        return _to_response(registry.get(market_id))
    except MarketNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
