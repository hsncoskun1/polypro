from dataclasses import dataclass

from app.domain.markets.exceptions import DuplicateMarketError, InvalidTimeframeError
from app.domain.markets.model import Market
from app.domain.markets.registry import InMemoryMarketRegistry, parse_timeframe


@dataclass
class DiscoveryItem:
    """Raw discovery input — unvalidated market candidate."""

    market_id: str
    title: str
    timeframe: str  # raw string, validated during discovery


@dataclass
class DiscoverySummary:
    added_count: int
    skipped_duplicate_count: int
    skipped_invalid_count: int
    total_seen: int


def run_discovery(
    items: list[DiscoveryItem], registry: InMemoryMarketRegistry
) -> DiscoverySummary:
    """Process discovery items against the registry.

    Valid, non-duplicate items are added. Duplicates and items with invalid
    timeframes are counted and reflected in the summary. No silent fallback.
    """
    added = 0
    skipped_duplicate = 0
    skipped_invalid = 0

    for item in items:
        try:
            timeframe = parse_timeframe(item.timeframe)
        except InvalidTimeframeError:
            skipped_invalid += 1
            continue

        market = Market(market_id=item.market_id, title=item.title, timeframe=timeframe)
        try:
            registry.add(market)
            added += 1
        except DuplicateMarketError:
            skipped_duplicate += 1

    return DiscoverySummary(
        added_count=added,
        skipped_duplicate_count=skipped_duplicate,
        skipped_invalid_count=skipped_invalid,
        total_seen=len(items),
    )
