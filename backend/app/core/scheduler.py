import threading
import time
from datetime import datetime, timezone
from typing import Any

from app.clients.polymarket import PolymarketClient
from app.core.config import POLYMARKET_URL
from app.core.logger import get_logger
from app.services.discovery_client import run_polymarket_fetch_to_discovery

logger = get_logger(__name__)


class DiscoveryScheduler:
    """Periodically triggers the discovery chain when enabled.

    On each tick:
    - If run_guard is busy: skip (a manual or prior scheduled run is in progress)
    - Otherwise: acquire guard, update status, run discovery, release guard

    Errors during a scheduled run are logged; the scheduler does not crash.
    Disabled by default — set DISCOVERY_SCHEDULER_ENABLED=true to activate.
    """

    def __init__(
        self,
        *,
        interval_seconds: int,
        enabled: bool,
        registry: Any,
        run_guard: Any,
        run_status: Any,
    ) -> None:
        self._interval = interval_seconds
        self._enabled = enabled
        self._registry = registry
        self._run_guard = run_guard
        self._run_status = run_status
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self._enabled:
            logger.info("Discovery scheduler disabled — skipping start")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="discovery-scheduler")
        self._thread.start()
        logger.info("Discovery scheduler started (interval=%ds)", self._interval)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        logger.info("Discovery scheduler stopped")

    def _loop(self) -> None:
        while not self._stop_event.wait(self._interval):
            self._tick()

    def _tick(self) -> None:
        if not self._run_guard.acquire():
            logger.info("Discovery scheduler: run guard busy, skipping tick")
            return
        self._run_status.is_running = True
        self._run_status.last_error = None
        try:
            client = PolymarketClient(POLYMARKET_URL)
            result = run_polymarket_fetch_to_discovery(client, self._registry)
            now = datetime.now(tz=timezone.utc)
            self._run_status.last_finished_at = now
            self._run_status.last_success_at = now
            self._run_status.last_result_summary = {
                "added_count": result.summary.added_count,
                "skipped_duplicate_count": result.summary.skipped_duplicate_count,
                "skipped_invalid_count": result.summary.skipped_invalid_count,
                "total_seen": result.summary.total_seen,
            }
            logger.info(
                "Discovery scheduler: run complete — added=%d, seen=%d",
                result.summary.added_count,
                result.summary.total_seen,
            )
        except Exception as exc:
            self._run_status.last_finished_at = datetime.now(tz=timezone.utc)
            self._run_status.last_error = str(exc)
            logger.error("Discovery scheduler: run failed — %s", exc)
        finally:
            self._run_status.is_running = False
            self._run_guard.release()
