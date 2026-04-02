from pydantic import BaseModel
from app.domain.markets.model import MarketStatus, Timeframe


class MarketCreate(BaseModel):
    market_id: str
    title: str
    timeframe: str


class StatusUpdate(BaseModel):
    status: MarketStatus


class MarketResponse(BaseModel):
    market_id: str
    title: str
    timeframe: Timeframe
    status: MarketStatus
