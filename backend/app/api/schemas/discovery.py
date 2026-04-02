from datetime import datetime

from pydantic import BaseModel, Field


class DiscoveryTriggerRequest(BaseModel):
    source_name: str = Field(default="polymarket", min_length=1)
    url: str | None = Field(default=None)
    timeout: float = Field(default=10.0, gt=0)


class DiscoverySummarySchema(BaseModel):
    added_count: int
    skipped_duplicate_count: int
    skipped_invalid_count: int
    total_seen: int


class DiscoveryTriggerResponse(BaseModel):
    summary: DiscoverySummarySchema
    source_name: str
    ran_at: datetime
