from datetime import date

import pytest

from app.clients.timeframe_mapping import TimeframeMappingError, map_end_date_to_timeframe
from app.domain.markets.model import Timeframe

REF = date(2026, 4, 2)  # fixed reference date for deterministic tests


class TestMapEndDateToTimeframe:
    def test_same_day_maps_to_1d(self):
        result = map_end_date_to_timeframe("2026-04-02", reference_date=REF)
        assert result == Timeframe.ONE_DAY

    def test_one_day_ahead_maps_to_1d(self):
        result = map_end_date_to_timeframe("2026-04-03", reference_date=REF)
        assert result == Timeframe.ONE_DAY

    def test_two_days_ahead_maps_to_1w(self):
        result = map_end_date_to_timeframe("2026-04-04", reference_date=REF)
        assert result == Timeframe.ONE_WEEK

    def test_seven_days_ahead_maps_to_1w(self):
        result = map_end_date_to_timeframe("2026-04-09", reference_date=REF)
        assert result == Timeframe.ONE_WEEK

    def test_eight_days_ahead_maps_to_1m(self):
        result = map_end_date_to_timeframe("2026-04-10", reference_date=REF)
        assert result == Timeframe.ONE_MONTH

    def test_thirty_days_ahead_maps_to_1m(self):
        result = map_end_date_to_timeframe("2026-05-02", reference_date=REF)
        assert result == Timeframe.ONE_MONTH

    def test_thirty_one_days_ahead_maps_to_3m(self):
        result = map_end_date_to_timeframe("2026-05-03", reference_date=REF)
        assert result == Timeframe.THREE_MONTHS

    def test_far_future_maps_to_3m(self):
        result = map_end_date_to_timeframe("2026-12-31", reference_date=REF)
        assert result == Timeframe.THREE_MONTHS

    def test_past_date_raises(self):
        with pytest.raises(TimeframeMappingError, match="in the past"):
            map_end_date_to_timeframe("2026-04-01", reference_date=REF)

    def test_unparseable_string_raises(self):
        with pytest.raises(TimeframeMappingError, match="Cannot parse"):
            map_end_date_to_timeframe("not-a-date", reference_date=REF)

    def test_empty_string_raises(self):
        with pytest.raises(TimeframeMappingError, match="Cannot parse"):
            map_end_date_to_timeframe("", reference_date=REF)

    def test_boundary_day_1_is_1d(self):
        """Explicit boundary: exactly 1 day → 1D."""
        result = map_end_date_to_timeframe("2026-04-03", reference_date=REF)
        assert result == Timeframe.ONE_DAY

    def test_boundary_day_2_is_1w(self):
        """Explicit boundary: exactly 2 days → 1W."""
        result = map_end_date_to_timeframe("2026-04-04", reference_date=REF)
        assert result == Timeframe.ONE_WEEK

    def test_boundary_day_30_is_1m(self):
        """Explicit boundary: exactly 30 days → 1M."""
        result = map_end_date_to_timeframe("2026-05-02", reference_date=REF)
        assert result == Timeframe.ONE_MONTH

    def test_boundary_day_31_is_3m(self):
        """Explicit boundary: exactly 31 days → 3M."""
        result = map_end_date_to_timeframe("2026-05-03", reference_date=REF)
        assert result == Timeframe.THREE_MONTHS
