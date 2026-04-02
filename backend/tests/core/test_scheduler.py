from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.core.run_guard import DiscoveryRunGuard
from app.core.run_status import DiscoveryRunStatus
from app.core.scheduler import DiscoveryScheduler

_TICK_PATCH = "app.core.scheduler.run_polymarket_fetch_to_discovery"
_CLIENT_PATCH = "app.core.scheduler.PolymarketClient"


def _make_scheduler(*, enabled=True, interval=60):
    registry = MagicMock()
    guard = DiscoveryRunGuard()
    status = DiscoveryRunStatus()
    scheduler = DiscoveryScheduler(
        interval_seconds=interval,
        enabled=enabled,
        registry=registry,
        run_guard=guard,
        run_status=status,
    )
    return scheduler, guard, status


def _make_result(added=0):
    from app.domain.markets.discovery import DiscoverySummary
    from app.services.discovery import DiscoveryResult
    return DiscoveryResult(
        summary=DiscoverySummary(
            added_count=added,
            skipped_duplicate_count=0,
            skipped_invalid_count=0,
            total_seen=added,
        ),
        source_name="polymarket",
        ran_at=datetime(2026, 4, 2, 12, 0, 0, tzinfo=timezone.utc),
    )


def test_scheduler_disabled_does_not_start_thread():
    scheduler, _, _ = _make_scheduler(enabled=False)
    scheduler.start()
    assert scheduler._thread is None
    scheduler.stop()


def test_scheduler_tick_calls_discovery_chain():
    scheduler, guard, status = _make_scheduler()
    with patch(_TICK_PATCH, return_value=_make_result(added=2)) as mock_fn, \
         patch(_CLIENT_PATCH):
        scheduler._tick()
    mock_fn.assert_called_once()


def test_scheduler_tick_updates_status_on_success():
    scheduler, guard, status = _make_scheduler()
    with patch(_TICK_PATCH, return_value=_make_result(added=3)), \
         patch(_CLIENT_PATCH):
        scheduler._tick()
    assert status.is_running is False
    assert status.last_success_at is not None
    assert status.last_finished_at is not None
    assert status.last_result_summary["added_count"] == 3
    assert status.last_error is None


def test_scheduler_tick_skips_when_guard_busy():
    scheduler, guard, status = _make_scheduler()
    guard.acquire()  # simulate a run already in progress
    try:
        with patch(_TICK_PATCH) as mock_fn:
            scheduler._tick()
        mock_fn.assert_not_called()
    finally:
        guard.release()


def test_scheduler_tick_releases_guard_after_success():
    scheduler, guard, status = _make_scheduler()
    with patch(_TICK_PATCH, return_value=_make_result()), \
         patch(_CLIENT_PATCH):
        scheduler._tick()
    assert guard.acquire() is True
    guard.release()


def test_scheduler_tick_records_error_on_failure():
    scheduler, guard, status = _make_scheduler()
    with patch(_TICK_PATCH, side_effect=Exception("boom")), \
         patch(_CLIENT_PATCH):
        scheduler._tick()
    assert status.last_error == "boom"
    assert status.last_finished_at is not None
    assert status.is_running is False


def test_scheduler_tick_releases_guard_after_error():
    scheduler, guard, status = _make_scheduler()
    with patch(_TICK_PATCH, side_effect=Exception("boom")), \
         patch(_CLIENT_PATCH):
        scheduler._tick()
    assert guard.acquire() is True
    guard.release()


def test_scheduler_is_running_false_after_tick():
    scheduler, guard, status = _make_scheduler()
    with patch(_TICK_PATCH, return_value=_make_result()), \
         patch(_CLIENT_PATCH):
        scheduler._tick()
    assert status.is_running is False


# ── Hardening ─────────────────────────────────────────────────────────────────

def test_scheduler_rejects_zero_interval():
    with pytest.raises(ValueError, match="interval_seconds"):
        _make_scheduler(interval=0)


def test_scheduler_rejects_negative_interval():
    with pytest.raises(ValueError, match="interval_seconds"):
        _make_scheduler(interval=-1)


def test_scheduler_accepts_minimum_interval():
    scheduler, _, _ = _make_scheduler(interval=1)
    assert scheduler._interval == 1


def test_scheduler_double_start_does_not_create_second_thread():
    scheduler, _, _ = _make_scheduler()
    scheduler.start()
    first_thread = scheduler._thread
    scheduler.start()  # second call — should be no-op
    assert scheduler._thread is first_thread
    scheduler.stop()


def test_scheduler_double_stop_is_safe():
    scheduler, _, _ = _make_scheduler()
    scheduler.start()
    scheduler.stop()
    scheduler.stop()  # second stop — should not raise


def test_scheduler_stop_when_never_started_is_safe():
    scheduler, _, _ = _make_scheduler(enabled=False)
    scheduler.start()  # no-op because disabled
    scheduler.stop()   # should not raise


def test_scheduler_thread_is_none_after_stop():
    scheduler, _, _ = _make_scheduler()
    scheduler.start()
    scheduler.stop()
    assert scheduler._thread is None


def test_scheduler_continues_after_tick_error():
    scheduler, guard, status = _make_scheduler()
    # First tick raises, second tick succeeds — guard must be released between them
    with patch(_TICK_PATCH, side_effect=Exception("first fail")), \
         patch(_CLIENT_PATCH):
        scheduler._tick()
    assert guard.acquire() is True  # guard released after error
    guard.release()
    with patch(_TICK_PATCH, return_value=_make_result(added=1)), \
         patch(_CLIENT_PATCH):
        scheduler._tick()
    assert status.last_success_at is not None
    assert status.last_error is None
