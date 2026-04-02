from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.clients.polymarket import PolymarketClient, PolymarketClientError

URL = "https://example.com/markets"


def _mock_response(status_code: int = 200, json_data=None, raise_for=None):
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    if raise_for is not None:
        mock.json.side_effect = raise_for
    return mock


class TestPolymarketClientFetch:
    def test_successful_fetch_returns_list(self):
        payload = [{"condition_id": "abc", "question": "Will X?", "end_date": "2026-01-01"}]
        with patch("httpx.get", return_value=_mock_response(200, payload)):
            result = PolymarketClient(URL).fetch()
        assert result == payload

    def test_empty_list_is_accepted(self):
        with patch("httpx.get", return_value=_mock_response(200, [])):
            result = PolymarketClient(URL).fetch()
        assert result == []

    def test_http_error_raises_client_error(self):
        with patch("httpx.get", return_value=_mock_response(500)):
            with pytest.raises(PolymarketClientError, match="HTTP 500"):
                PolymarketClient(URL).fetch()

    def test_http_404_raises_client_error(self):
        with patch("httpx.get", return_value=_mock_response(404)):
            with pytest.raises(PolymarketClientError, match="HTTP 404"):
                PolymarketClient(URL).fetch()

    def test_timeout_raises_client_error(self):
        with patch("httpx.get", side_effect=httpx.TimeoutException("timed out")):
            with pytest.raises(PolymarketClientError, match="timed out"):
                PolymarketClient(URL).fetch()

    def test_request_error_raises_client_error(self):
        with patch("httpx.get", side_effect=httpx.RequestError("connection refused")):
            with pytest.raises(PolymarketClientError, match="Request failed"):
                PolymarketClient(URL).fetch()

    def test_invalid_json_raises_client_error(self):
        with patch(
            "httpx.get",
            return_value=_mock_response(200, raise_for=ValueError("bad json")),
        ):
            with pytest.raises(PolymarketClientError, match="Failed to parse JSON"):
                PolymarketClient(URL).fetch()

    def test_non_list_json_raises_client_error(self):
        with patch("httpx.get", return_value=_mock_response(200, {"key": "value"})):
            with pytest.raises(PolymarketClientError, match="Expected JSON list"):
                PolymarketClient(URL).fetch()
