import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from app.core.logger import get_logger
from app.domain.markets.registry import InMemoryMarketRegistry
from app.persistence.markets import JsonMarketStore

logger = get_logger(__name__)

_DEFAULT_STORE_PATH = "data/markets.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    store_path = os.environ.get("MARKET_STORE_PATH", _DEFAULT_STORE_PATH)
    store = JsonMarketStore(store_path)
    registry = InMemoryMarketRegistry()
    for market in store.load():
        registry.add(market)
    app.state.market_registry = registry
    app.state.market_store = store
    logger.info("POLYPRO backend starting up")
    yield


app = FastAPI(title="POLYPRO", version="0.2.3", lifespan=lifespan)
app.include_router(health_router)
app.include_router(markets_router)
