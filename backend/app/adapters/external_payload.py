from dataclasses import dataclass

from app.adapters.discovery import RawPayloadItem
from app.clients.timeframe_mapping import map_end_date_to_timeframe


class ExternalPayloadMappingError(Exception):
    """Raised when an external payload item cannot be mapped to a RawPayloadItem."""


@dataclass
class PolymarketMarketPayload:
    """External Polymarket payload format shell.

    Field names approximate real Polymarket API response structure.
    Actual field names and types will be refined when HTTP integration is added.

    condition_id → market_id
    question     → title
    end_date     → timeframe (ISO 8601 date string, converted via map_end_date_to_timeframe)
    """

    condition_id: str
    question: str
    end_date: str


def map_to_raw_payload_item(payload: PolymarketMarketPayload) -> RawPayloadItem:
    """Map a PolymarketMarketPayload to a RawPayloadItem.

    Raises ExternalPayloadMappingError if any required field is empty or whitespace-only.
    Raises TimeframeMappingError (from timeframe_mapping) if end_date is a past date
    or cannot be parsed as ISO 8601. No silent fallback.
    """
    condition_id = payload.condition_id.strip()
    question = payload.question.strip()
    end_date = payload.end_date.strip()

    if not condition_id:
        raise ExternalPayloadMappingError("condition_id is empty")
    if not question:
        raise ExternalPayloadMappingError(f"question is empty (condition_id={condition_id!r})")
    if not end_date:
        raise ExternalPayloadMappingError(f"end_date is empty (condition_id={condition_id!r})")

    timeframe = map_end_date_to_timeframe(end_date)

    return RawPayloadItem(
        market_id=condition_id,
        title=question,
        timeframe=timeframe.value,
    )
