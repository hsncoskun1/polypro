import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.discovery import router as discovery_router
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from app.api.admin_control_plane import router as admin_control_plane_router
from app.api.control_plane import router as control_plane_router
from app.api.readiness import router as readiness_router
from app.api.settings import router as settings_router
from app.api.auth import router as auth_router
from app.api.admin_users import router as admin_users_router
from app.api.user_entitlement import router as user_entitlement_router
from app.api.launcher import router as launcher_router
from app.api.deps import require_launcher_grant
from fastapi import Depends
from app.core.config import DISCOVERY_SCHEDULER_ENABLED, DISCOVERY_SCHEDULER_INTERVAL
from app.core.logger import get_logger
from app.core.run_guard import DiscoveryRunGuard
from app.core.run_status import DiscoveryRunStatus
from app.core.scheduler import DiscoveryScheduler
from app.domain.markets.registry import InMemoryMarketRegistry
from app.persistence.markets import SqliteMarketStore
from app.persistence.auth_store import AuthStore

logger = get_logger(__name__)

_DEFAULT_STORE_PATH = "data/markets.db"
_DEFAULT_AUTH_DB_PATH = "data/auth.db"


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
    auth_db_path = os.environ.get("AUTH_DB_PATH", _DEFAULT_AUTH_DB_PATH)
    app.state.auth_store = AuthStore(db_path=auth_db_path)
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(readiness_router)
app.include_router(launcher_router)
app.include_router(auth_router)
app.include_router(settings_router)
app.include_router(markets_router)
app.include_router(discovery_router)
app.include_router(control_plane_router, dependencies=[Depends(require_launcher_grant)])
app.include_router(admin_control_plane_router, dependencies=[Depends(require_launcher_grant)])
app.include_router(admin_users_router, dependencies=[Depends(require_launcher_grant)])
app.include_router(user_entitlement_router, dependencies=[Depends(require_launcher_grant)])
