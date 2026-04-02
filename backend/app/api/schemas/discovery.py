from datetime import datetime

from pydantic import BaseModel, Field


class RawMarketItemSchema(BaseModel):
    market_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)


class DiscoveryTriggerRequest(BaseModel):
    source_name: str = Field(default="unknown", min_length=1)
    items: list[RawMarketItemSchema]


class DiscoverySummarySchema(BaseModel):
    added_count: int
    skipped_duplicate_count: int
    skipped_invalid_count: int
    total_seen: int


class DiscoveryTriggerResponse(BaseModel):
    summary: DiscoverySummarySchema
    source_name: str
    ran_at: datetime
