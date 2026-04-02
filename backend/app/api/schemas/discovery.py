from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DiscoveryTriggerRequest(BaseModel):
    source_name: str = Field(default="polymarket", min_length=1)
    url: str | None = Field(default=None)
    timeout: float = Field(default=10.0, gt=0, le=60.0)


class DiscoverySummarySchema(BaseModel):
    added_count: int
    skipped_duplicate_count: int
    skipped_invalid_count: int
    total_seen: int


class DiscoveryTriggerResponse(BaseModel):
    summary: DiscoverySummarySchema
    source_name: str
    ran_at: datetime


class DiscoveryRunStatusResponse(BaseModel):
    is_running: bool
    last_finished_at: datetime | None = None
    last_success_at: datetime | None = None
    last_result_summary: dict[str, Any] | None = None
    last_error: str | None = None
