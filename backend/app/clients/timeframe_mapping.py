from datetime import date

from app.domain.markets.model import Timeframe


class TimeframeMappingError(Exception):
    """Raised when an end_date string cannot be mapped to a supported Timeframe."""


def map_end_date_to_timeframe(
    end_date: str,
    reference_date: date | None = None,
) -> Timeframe:
    """Map an ISO 8601 date string to a Timeframe based on days remaining.

    Thresholds (days from reference_date to end_date):
      0–1   → 1D
      2–7   → 1W
      8–30  → 1M
      31+   → 3M

    Raises TimeframeMappingError if end_date is in the past or cannot be parsed.
    reference_date defaults to today; pass an explicit value for deterministic tests.
    """
    if reference_date is None:
        reference_date = date.today()

    try:
        target = date.fromisoformat(end_date)
    except (ValueError, TypeError) as exc:
        raise TimeframeMappingError(
            f"Cannot parse end_date as ISO 8601 date: {end_date!r}"
        ) from exc

    delta = (target - reference_date).days

    if delta < 0:
        raise TimeframeMappingError(
            f"end_date {end_date!r} is in the past (delta={delta} days)"
        )
    if delta <= 1:
        return Timeframe.ONE_DAY
    if delta <= 7:
        return Timeframe.ONE_WEEK
    if delta <= 30:
        return Timeframe.ONE_MONTH
    return Timeframe.THREE_MONTHS
