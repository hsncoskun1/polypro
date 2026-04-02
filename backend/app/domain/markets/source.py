from typing import Protocol

from app.domain.markets.discovery import DiscoveryItem, DiscoverySummary, run_discovery
from app.domain.markets.registry import InMemoryMarketRegistry


class DiscoverySource(Protocol):
    """Contract for discovery input providers."""

    def fetch(self) -> list[DiscoveryItem]:
        ...


class StubDiscoverySource:
    """Static in-memory source — used for testing and shell development."""

    def __init__(self, items: list[DiscoveryItem]) -> None:
        self._items = items

    def fetch(self) -> list[DiscoveryItem]:
        return list(self._items)


def run_discovery_from_source(
    source: DiscoverySource, registry: InMemoryMarketRegistry
) -> DiscoverySummary:
    """Run discovery using a source contract instead of a raw item list."""
    return run_discovery(source.fetch(), registry)
