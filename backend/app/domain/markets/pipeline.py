from typing import Protocol

from app.domain.markets.discovery import DiscoverySummary
from app.domain.markets.normalize import RawMarketItem, run_discovery_from_raw
from app.domain.markets.registry import InMemoryMarketRegistry


class RawDiscoverySource(Protocol):
    """Contract for raw discovery input providers.

    Returns unvalidated RawMarketItem instances — normalization happens
    inside the pipeline.
    """

    def fetch(self) -> list[RawMarketItem]:
        ...


class StubRawDiscoverySource:
    """Static in-memory raw source — used for pipeline testing."""

    def __init__(self, items: list[RawMarketItem]) -> None:
        self._items = items

    def fetch(self) -> list[RawMarketItem]:
        return list(self._items)


def run_pipeline(
    source: RawDiscoverySource, registry: InMemoryMarketRegistry
) -> DiscoverySummary:
    """Full discovery pipeline: source → normalize → discover.

    Fetches raw items from source, normalizes each, and applies to the
    registry. Returns a unified DiscoverySummary covering all stages.
    """
    return run_discovery_from_raw(source.fetch(), registry)
