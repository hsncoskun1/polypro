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
