import pytest
from app.adapters.external_payload import (
    ExternalPayloadMappingError,
    PolymarketMarketPayload,
    map_to_raw_payload_item,
)
from app.adapters.discovery import RawPayloadItem


def test_valid_payload_maps_correctly():
    payload = PolymarketMarketPayload(
        condition_id="cond-001",
        question="Will ETH hit $5k?",
        end_date="1W",
    )
    result = map_to_raw_payload_item(payload)
    assert isinstance(result, RawPayloadItem)
    assert result.market_id == "cond-001"
    assert result.title == "Will ETH hit $5k?"
    assert result.timeframe == "1W"


def test_whitespace_is_stripped_from_all_fields():
    payload = PolymarketMarketPayload(
        condition_id="  cond-002  ",
        question="  Some question  ",
        end_date="  1D  ",
    )
    result = map_to_raw_payload_item(payload)
    assert result.market_id == "cond-002"
    assert result.title == "Some question"
    assert result.timeframe == "1D"


def test_empty_condition_id_raises_mapping_error():
    payload = PolymarketMarketPayload(condition_id="", question="Q", end_date="1W")
    with pytest.raises(ExternalPayloadMappingError, match="condition_id is empty"):
        map_to_raw_payload_item(payload)


def test_whitespace_only_condition_id_raises_mapping_error():
    payload = PolymarketMarketPayload(condition_id="   ", question="Q", end_date="1W")
    with pytest.raises(ExternalPayloadMappingError, match="condition_id is empty"):
        map_to_raw_payload_item(payload)


def test_empty_question_raises_mapping_error():
    payload = PolymarketMarketPayload(condition_id="cond-001", question="", end_date="1W")
    with pytest.raises(ExternalPayloadMappingError, match="question is empty"):
        map_to_raw_payload_item(payload)


def test_empty_end_date_raises_mapping_error():
    payload = PolymarketMarketPayload(condition_id="cond-001", question="Q", end_date="")
    with pytest.raises(ExternalPayloadMappingError, match="end_date is empty"):
        map_to_raw_payload_item(payload)


def test_mixed_payload_list_maps_valid_and_raises_on_invalid():
    payloads = [
        PolymarketMarketPayload(condition_id="c1", question="Q1", end_date="1W"),
        PolymarketMarketPayload(condition_id="", question="Q2", end_date="1W"),
        PolymarketMarketPayload(condition_id="c3", question="Q3", end_date="1D"),
    ]
    results = []
    errors = 0
    for p in payloads:
        try:
            results.append(map_to_raw_payload_item(p))
        except ExternalPayloadMappingError:
            errors += 1

    assert len(results) == 2
    assert errors == 1
    assert results[0].market_id == "c1"
    assert results[1].market_id == "c3"
