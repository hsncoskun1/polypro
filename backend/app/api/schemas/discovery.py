from datetime import datetime

from pydantic import BaseModel


class RawMarketItemSchema(BaseModel):
    market_id: str
    title: str
    timeframe: str


class DiscoveryTriggerRequest(BaseModel):
    source_name: str = "unknown"
    items: list[RawMarketItemSchema] = []


class DiscoverySummarySchema(BaseModel):
    added_count: int
    skipped_duplicate_count: int
    skipped_invalid_count: int
    total_seen: int


class DiscoveryTriggerResponse(BaseModel):
    summary: DiscoverySummarySchema
    source_name: str
    ran_at: datetime
