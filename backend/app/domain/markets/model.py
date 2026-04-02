from dataclasses import dataclass
from enum import Enum


class Timeframe(str, Enum):
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    ONE_MONTH = "1M"
    THREE_MONTHS = "3M"


class MarketStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class Market:
    market_id: str
    title: str
    timeframe: Timeframe
    status: MarketStatus = MarketStatus.ACTIVE
