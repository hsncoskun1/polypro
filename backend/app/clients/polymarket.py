import httpx


class PolymarketClientError(Exception):
    """Raised when the Polymarket client fails to fetch or parse a response."""


class PolymarketClient:
    """Minimal HTTP client shell for fetching raw Polymarket market data.

    Fetches JSON from a URL and returns the parsed list of market dicts.
    No auth, no retry, no backoff. Raises PolymarketClientError on any failure.
    Not wired to the discovery pipeline — shell only.
    """

    def __init__(self, url: str, timeout: float = 10.0) -> None:
        self._url = url
        self._timeout = timeout

    def fetch(self) -> list[dict]:
        try:
            response = httpx.get(self._url, timeout=self._timeout)
        except httpx.TimeoutException as exc:
            raise PolymarketClientError(f"Request timed out: {self._url}") from exc
        except httpx.RequestError as exc:
            raise PolymarketClientError(f"Request failed: {exc}") from exc

        if response.status_code != 200:
            raise PolymarketClientError(
                f"HTTP {response.status_code} from {self._url}"
            )

        try:
            data = response.json()
        except Exception as exc:
            raise PolymarketClientError(f"Failed to parse JSON response: {exc}") from exc

        if not isinstance(data, list):
            raise PolymarketClientError(
                f"Expected JSON list, got {type(data).__name__}"
            )

        return data
