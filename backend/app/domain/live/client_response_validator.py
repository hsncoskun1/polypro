"""Client response validator — v0.8.1.

Validates ExternalResponsePayload instances before they are passed to
the response mapper. Any missing required field causes validation_passed=False
and the operation is treated as fail-closed (TERMINAL_FAILURE path).

Unknown or structurally invalid responses are never forwarded as success.
"""
from typing import List, Tuple
from app.domain.live.external_response_payload import ExternalResponsePayload


def validate_submit_response(
    payload: ExternalResponsePayload,
) -> Tuple[bool, List[str]]:
    """Validate an inbound submit response payload.

    Required fields: mapped_order_id, mapped_status.

    Returns:
        (validation_passed, blocker_reasons)
    """
    blockers: List[str] = []
    if not payload.mapped_order_id:
        blockers.append("missing_required_response_fields:mapped_order_id")
    if not payload.mapped_status and not payload.terminal_failure:
        blockers.append("missing_required_response_fields:mapped_status")
    return (len(blockers) == 0, blockers)


def validate_cancel_response(
    payload: ExternalResponsePayload,
) -> Tuple[bool, List[str]]:
    """Validate an inbound cancel response payload.

    Required fields: mapped_order_id, mapped_status.

    Returns:
        (validation_passed, blocker_reasons)
    """
    blockers: List[str] = []
    if not payload.mapped_order_id:
        blockers.append("missing_required_response_fields:mapped_order_id")
    if not payload.mapped_status and not payload.terminal_failure:
        blockers.append("missing_required_response_fields:mapped_status")
    return (len(blockers) == 0, blockers)


def validate_replace_response(
    payload: ExternalResponsePayload,
) -> Tuple[bool, List[str]]:
    """Validate an inbound replace response payload.

    Required fields: mapped_order_id, mapped_status.

    Returns:
        (validation_passed, blocker_reasons)
    """
    blockers: List[str] = []
    if not payload.mapped_order_id:
        blockers.append("missing_required_response_fields:mapped_order_id")
    if not payload.mapped_status and not payload.terminal_failure:
        blockers.append("missing_required_response_fields:mapped_status")
    return (len(blockers) == 0, blockers)


def validate_update_response(
    payload: ExternalResponsePayload,
) -> Tuple[bool, List[str]]:
    """Validate an inbound order-update response payload.

    Required fields: mapped_status.

    Returns:
        (validation_passed, blocker_reasons)
    """
    blockers: List[str] = []
    if not payload.mapped_status and not payload.terminal_failure:
        blockers.append("missing_required_response_fields:mapped_status")
    return (len(blockers) == 0, blockers)
