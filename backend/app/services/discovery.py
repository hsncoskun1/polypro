from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.markets.discovery import DiscoverySummary
from app.domain.markets.pipeline import RawDiscoverySource, run_pipeline
from app.domain.markets.registry import InMemoryMarketRegistry


@dataclass
class DiscoveryResult:
    """Application service result: pipeline summary plus run metadata."""

    summary: DiscoverySummary
    source_name: str
    ran_at: datetime


def run_discovery_service(
    source: RawDiscoverySource,
    registry: InMemoryMarketRegistry,
    *,
    source_name: str = "unknown",
) -> DiscoveryResult:
    """Run the discovery pipeline and return a result with metadata.

    Delegates entirely to run_pipeline(). Adds source_name and ran_at so
    callers (API, scheduler, admin trigger) have a consistent result envelope
    without reaching into pipeline internals.
    """
    summary = run_pipeline(source, registry)
    return DiscoveryResult(
        summary=summary,
        source_name=source_name,
        ran_at=datetime.now(UTC),
    )
