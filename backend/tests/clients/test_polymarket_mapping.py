import pytest

from app.adapters.external_payload import PolymarketMarketPayload
from app.clients.polymarket_mapping import (
    ClientPayloadMappingError,
    map_client_rows_to_payloads,
)


class TestMapClientRowsToPayloads:
    def test_valid_row_maps_to_payload(self):
        rows = [{"condition_id": "abc123", "question": "Will X?", "end_date": "2026-01-01"}]
        result = map_client_rows_to_payloads(rows)
        assert len(result) == 1
        assert isinstance(result[0], PolymarketMarketPayload)
        assert result[0].condition_id == "abc123"
        assert result[0].question == "Will X?"
        assert result[0].end_date == "2026-01-01"

    def test_multiple_valid_rows_map_correctly(self):
        rows = [
            {"condition_id": "a1", "question": "Q1?", "end_date": "2026-01-01"},
            {"condition_id": "b2", "question": "Q2?", "end_date": "2026-06-01"},
        ]
        result = map_client_rows_to_payloads(rows)
        assert len(result) == 2
        assert result[0].condition_id == "a1"
        assert result[1].condition_id == "b2"

    def test_empty_list_returns_empty(self):
        assert map_client_rows_to_payloads([]) == []

    def test_whitespace_values_passed_as_is(self):
        rows = [{"condition_id": "  abc  ", "question": "  Q?  ", "end_date": "  2026-01-01  "}]
        result = map_client_rows_to_payloads(rows)
        assert result[0].condition_id == "  abc  "
        assert result[0].question == "  Q?  "
        assert result[0].end_date == "  2026-01-01  "

    def test_missing_condition_id_raises(self):
        rows = [{"question": "Q?", "end_date": "2026-01-01"}]
        with pytest.raises(ClientPayloadMappingError, match="condition_id"):
            map_client_rows_to_payloads(rows)

    def test_missing_question_raises(self):
        rows = [{"condition_id": "abc", "end_date": "2026-01-01"}]
        with pytest.raises(ClientPayloadMappingError, match="question"):
            map_client_rows_to_payloads(rows)

    def test_missing_end_date_raises(self):
        rows = [{"condition_id": "abc", "question": "Q?"}]
        with pytest.raises(ClientPayloadMappingError, match="end_date"):
            map_client_rows_to_payloads(rows)

    def test_mixed_list_raises_on_invalid_row(self):
        rows = [
            {"condition_id": "a1", "question": "Q1?", "end_date": "2026-01-01"},
            {"condition_id": "b2", "question": "Q2?"},  # missing end_date
        ]
        with pytest.raises(ClientPayloadMappingError, match="Row 1.*end_date"):
            map_client_rows_to_payloads(rows)
