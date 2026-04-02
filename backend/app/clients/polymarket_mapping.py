from app.adapters.external_payload import PolymarketMarketPayload


class ClientPayloadMappingError(Exception):
    """Raised when a client response dict cannot be mapped to PolymarketMarketPayload."""


def map_client_rows_to_payloads(rows: list[dict]) -> list[PolymarketMarketPayload]:
    """Map raw client response rows to PolymarketMarketPayload instances.

    Reads condition_id, question, and end_date from each dict.
    Passes values as-is — whitespace normalization is the external payload contract's job.
    Raises ClientPayloadMappingError if a required field is missing from a row.
    No silent fallback. Not wired to trigger/service/adapter chain.
    """
    results = []
    for i, row in enumerate(rows):
        for field in ("condition_id", "question", "end_date"):
            if field not in row:
                raise ClientPayloadMappingError(
                    f"Row {i} missing required field '{field}'"
                )
        results.append(
            PolymarketMarketPayload(
                condition_id=row["condition_id"],
                question=row["question"],
                end_date=row["end_date"],
            )
        )
    return results
