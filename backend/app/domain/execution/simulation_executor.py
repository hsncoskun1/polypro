"""Simulation executor — paper trade entry and exit for simulation mode.

Design decisions:
- Never returns None. All paths return a fully populated ExecutionResult.
- Execution comes after verification gate; does not bypass it.
- Runtime state (lock) is passed in, not mutated globally.
- Order IDs are deterministic: PAPER-ENTRY-{event_key}-{side}
  and PAPER-EXIT-{event_key}-{side}. This supports idempotency analysis.
- Duplicate entry for the same event_key is blocked via ExecutionLock.
- Force sell, stop loss, take profit: NOT in scope (v0.5.1+).
- Real DB writes: NOT in scope (v0.5.2+). Lock is in-memory seam only.
"""
from app.domain.execution.execution_lock import ExecutionLock
from app.domain.execution.execution_request import ExecutionRequest
from app.domain.execution.execution_result import ExecutionResult


def simulate_entry(request: ExecutionRequest, lock: ExecutionLock) -> ExecutionResult:
    """Execute a simulation entry for the given request.

    Returns a blocked result if the event_key already has an open position.
    Acquires the lock on success so subsequent entry attempts are rejected.

    Args:
        request: The execution request with event, side, size, and fill price.
        lock: The execution lock to check and acquire.

    Returns:
        ExecutionResult with success=True on entry, or success=False with
        reason="duplicate_entry_blocked" if the event_key is already locked.
    """
    if lock.is_locked(request.event_key):
        return ExecutionResult(
            success=False,
            order_id="",
            fill_price=0.0,
            side=request.side,
            size=0.0,
            reason="duplicate_entry_blocked",
        )

    lock.acquire(request.event_key)
    return ExecutionResult(
        success=True,
        order_id=f"PAPER-ENTRY-{request.event_key}-{request.side}",
        fill_price=request.simulated_fill_price,
        side=request.side,
        size=request.requested_size,
        reason="",
    )


def simulate_exit(request: ExecutionRequest, lock: ExecutionLock) -> ExecutionResult:
    """Execute a simulation exit for the given request.

    Releases the lock for the event_key so a new entry can be made later.
    Exit always succeeds — there is no precondition check on lock state
    in this version, as exit can be called to close any open position.

    Args:
        request: The execution request with event, side, size, and fill price.
        lock: The execution lock to release.

    Returns:
        ExecutionResult with success=True and paper exit order details.
    """
    lock.release(request.event_key)
    return ExecutionResult(
        success=True,
        order_id=f"PAPER-EXIT-{request.event_key}-{request.side}",
        fill_price=request.simulated_fill_price,
        side=request.side,
        size=request.requested_size,
        reason="",
    )
