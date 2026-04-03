import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.discovery import router as discovery_router
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from app.api.readiness import router as readiness_router
from app.core.config import DISCOVERY_SCHEDULER_ENABLED, DISCOVERY_SCHEDULER_INTERVAL
from app.core.logger import get_logger
from app.core.run_guard import DiscoveryRunGuard
from app.core.run_status import DiscoveryRunStatus
from app.core.scheduler import DiscoveryScheduler
from app.domain.markets.registry import InMemoryMarketRegistry
from app.persistence.markets import SqliteMarketStore

logger = get_logger(__name__)

_DEFAULT_STORE_PATH = "data/markets.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    store_path = os.environ.get("MARKET_STORE_PATH", _DEFAULT_STORE_PATH)
    store = SqliteMarketStore(store_path)
    registry = InMemoryMarketRegistry()
    for market in store.load():
        registry.add(market)
    app.state.market_registry = registry
    app.state.market_store = store
    app.state.discovery_run_guard = DiscoveryRunGuard()
    app.state.discovery_run_status = DiscoveryRunStatus()
    scheduler = DiscoveryScheduler(
        interval_seconds=DISCOVERY_SCHEDULER_INTERVAL,
        enabled=DISCOVERY_SCHEDULER_ENABLED,
        registry=registry,
        run_guard=app.state.discovery_run_guard,
        run_status=app.state.discovery_run_status,
    )
    app.state.discovery_scheduler = scheduler
    scheduler.start()
    logger.info("POLYPRO backend starting up")
    yield
    scheduler.stop()


app = FastAPI(title="POLYPRO", version="0.3.1", lifespan=lifespan)
app.include_router(health_router)
app.include_router(readiness_router)
app.include_router(markets_router)
app.include_router(discovery_router)
