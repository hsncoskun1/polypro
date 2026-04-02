from dataclasses import dataclass

from app.domain.markets.discovery import DiscoveryItem, DiscoverySummary, run_discovery
from app.domain.markets.registry import InMemoryMarketRegistry


class NormalizationError(Exception):
    """Raised when a raw item cannot be normalized into a valid DiscoveryItem."""


@dataclass
class RawMarketItem:
    """Unvalidated raw input from an external source.

    Fields may contain leading/trailing whitespace or be empty.
    Normalization happens in normalize_item().
    """

    market_id: str
    title: str
    timeframe: str


def normalize_item(raw: RawMarketItem) -> DiscoveryItem:
    """Normalize a RawMarketItem into a DiscoveryItem.

    Strips whitespace from all fields. Raises NormalizationError if any
    required field is empty after stripping.
    """
    market_id = raw.market_id.strip()
    title = raw.title.strip()
    timeframe = raw.timeframe.strip()

    if not market_id:
        raise NormalizationError("market_id is empty")
    if not title:
        raise NormalizationError(f"title is empty (market_id={market_id!r})")
    if not timeframe:
        raise NormalizationError(f"timeframe is empty (market_id={market_id!r})")

    return DiscoveryItem(market_id=market_id, title=title, timeframe=timeframe)


def run_discovery_from_raw(
    raw_items: list[RawMarketItem], registry: InMemoryMarketRegistry
) -> DiscoverySummary:
    """Normalize raw items and run discovery against the registry.

    Normalization failures are counted in skipped_invalid_count.
    total_seen reflects all raw items, including those that failed normalization.
    No silent fallback — all failures are counted.
    """
    normalized: list[DiscoveryItem] = []
    normalization_failures = 0

    for raw in raw_items:
        try:
            normalized.append(normalize_item(raw))
        except NormalizationError:
            normalization_failures += 1

    summary = run_discovery(normalized, registry)

    return DiscoverySummary(
        added_count=summary.added_count,
        skipped_duplicate_count=summary.skipped_duplicate_count,
        skipped_invalid_count=summary.skipped_invalid_count + normalization_failures,
        total_seen=len(raw_items),
    )
