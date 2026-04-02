"""Tests for simulation executor — ExecutionRequest, ExecutionResult,
ExecutionLock, simulate_entry(), simulate_exit()."""
import pytest
from app.domain.execution.execution_lock import ExecutionLock
from app.domain.execution.execution_request import ExecutionRequest
from app.domain.execution.execution_result import ExecutionResult
from app.domain.execution.simulation_executor import simulate_entry, simulate_exit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(event_key="EVT-001", side="YES", size=10.0, price=0.65):
    return ExecutionRequest(
        event_key=event_key,
        side=side,
        requested_size=size,
        simulated_fill_price=price,
    )


def _fresh_lock():
    return ExecutionLock()


# ---------------------------------------------------------------------------
# TestExecutionRequest
# ---------------------------------------------------------------------------

class TestExecutionRequest:
    def test_fields_are_set_correctly(self):
        req = ExecutionRequest(
            event_key="EVT-X",
            side="NO",
            requested_size=5.0,
            simulated_fill_price=0.45,
        )
        assert req.event_key == "EVT-X"
        assert req.side == "NO"
        assert req.requested_size == 5.0
        assert req.simulated_fill_price == 0.45


# ---------------------------------------------------------------------------
# TestExecutionResult
# ---------------------------------------------------------------------------

class TestExecutionResult:
    def test_success_result_has_expected_fields(self):
        result = ExecutionResult(
            success=True,
            order_id="PAPER-ENTRY-EVT-001-YES",
            fill_price=0.65,
            side="YES",
            size=10.0,
        )
        assert result.success is True
        assert result.order_id == "PAPER-ENTRY-EVT-001-YES"
        assert result.fill_price == 0.65
        assert result.side == "YES"
        assert result.size == 10.0
        assert result.reason == ""

    def test_failure_result_has_reason(self):
        result = ExecutionResult(
            success=False,
            order_id="",
            fill_price=0.0,
            side="YES",
            size=0.0,
            reason="duplicate_entry_blocked",
        )
        assert result.success is False
        assert result.reason == "duplicate_entry_blocked"
        assert result.order_id == ""

    def test_result_is_never_none(self):
        result = ExecutionResult(
            success=True, order_id="X", fill_price=0.5, side="YES", size=1.0
        )
        assert result is not None


# ---------------------------------------------------------------------------
# TestExecutionLock
# ---------------------------------------------------------------------------

class TestExecutionLock:
    def test_new_lock_is_not_locked(self):
        lock = _fresh_lock()
        assert lock.is_locked("EVT-001") is False

    def test_acquire_locks_event(self):
        lock = _fresh_lock()
        lock.acquire("EVT-001")
        assert lock.is_locked("EVT-001") is True

    def test_release_unlocks_event(self):
        lock = _fresh_lock()
        lock.acquire("EVT-001")
        lock.release("EVT-001")
        assert lock.is_locked("EVT-001") is False

    def test_release_on_unlocked_event_is_safe(self):
        lock = _fresh_lock()
        lock.release("EVT-NOT-LOCKED")  # must not raise
        assert lock.is_locked("EVT-NOT-LOCKED") is False


# ---------------------------------------------------------------------------
# TestSimulateEntry
# ---------------------------------------------------------------------------

class TestSimulateEntry:
    def test_entry_success_returns_result(self):
        lock = _fresh_lock()
        result = simulate_entry(_make_request(), lock)
        assert result.success is True
        assert result.order_id == "PAPER-ENTRY-EVT-001-YES"
        assert result.fill_price == 0.65
        assert result.side == "YES"
        assert result.size == 10.0
        assert result.reason == ""

    def test_entry_result_is_never_none(self):
        lock = _fresh_lock()
        result = simulate_entry(_make_request(), lock)
        assert result is not None

    def test_entry_acquires_lock(self):
        lock = _fresh_lock()
        simulate_entry(_make_request(), lock)
        assert lock.is_locked("EVT-001") is True

    def test_duplicate_entry_is_blocked(self):
        lock = _fresh_lock()
        simulate_entry(_make_request(), lock)
        result = simulate_entry(_make_request(), lock)
        assert result.success is False
        assert result.reason == "duplicate_entry_blocked"

    def test_duplicate_entry_returns_zero_fill(self):
        lock = _fresh_lock()
        simulate_entry(_make_request(), lock)
        result = simulate_entry(_make_request(), lock)
        assert result.fill_price == 0.0
        assert result.size == 0.0
        assert result.order_id == ""

    def test_different_events_are_not_blocked(self):
        lock = _fresh_lock()
        simulate_entry(_make_request(event_key="EVT-001"), lock)
        result = simulate_entry(_make_request(event_key="EVT-002"), lock)
        assert result.success is True

    def test_paper_order_id_format(self):
        lock = _fresh_lock()
        result = simulate_entry(_make_request(event_key="EVT-ABC", side="NO"), lock)
        assert result.order_id == "PAPER-ENTRY-EVT-ABC-NO"


# ---------------------------------------------------------------------------
# TestSimulateExit
# ---------------------------------------------------------------------------

class TestSimulateExit:
    def test_exit_success_returns_result(self):
        lock = _fresh_lock()
        simulate_entry(_make_request(), lock)
        result = simulate_exit(_make_request(price=0.80), lock)
        assert result.success is True
        assert result.order_id == "PAPER-EXIT-EVT-001-YES"
        assert result.fill_price == 0.80
        assert result.reason == ""

    def test_exit_result_is_never_none(self):
        lock = _fresh_lock()
        result = simulate_exit(_make_request(), lock)
        assert result is not None

    def test_exit_releases_lock(self):
        lock = _fresh_lock()
        simulate_entry(_make_request(), lock)
        simulate_exit(_make_request(), lock)
        assert lock.is_locked("EVT-001") is False

    def test_entry_allowed_after_exit(self):
        lock = _fresh_lock()
        simulate_entry(_make_request(), lock)
        simulate_exit(_make_request(), lock)
        result = simulate_entry(_make_request(), lock)
        assert result.success is True

    def test_paper_exit_order_id_format(self):
        lock = _fresh_lock()
        result = simulate_exit(_make_request(event_key="EVT-Z", side="NO"), lock)
        assert result.order_id == "PAPER-EXIT-EVT-Z-NO"


# ---------------------------------------------------------------------------
# TestIdempotency
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_repeated_entry_returns_blocked_not_none(self):
        """Idempotent re-call on entry must return a blocked result, not None."""
        lock = _fresh_lock()
        simulate_entry(_make_request(), lock)
        result = simulate_entry(_make_request(), lock)
        assert result is not None
        assert result.success is False
        assert result.reason == "duplicate_entry_blocked"

    def test_repeated_exit_is_safe(self):
        """Repeated exit calls must not raise — lock.release is idempotent."""
        lock = _fresh_lock()
        simulate_entry(_make_request(), lock)
        simulate_exit(_make_request(), lock)
        result = simulate_exit(_make_request(), lock)  # second exit
        assert result is not None
        assert result.success is True
