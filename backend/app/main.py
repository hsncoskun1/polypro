from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from app.core.logger import get_logger
from app.domain.markets.registry import InMemoryMarketRegistry

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.market_registry = InMemoryMarketRegistry()
    logger.info("POLYPRO backend starting up")
    yield


app = FastAPI(title="POLYPRO", version="0.2.1", lifespan=lifespan)
app.include_router(health_router)
app.include_router(markets_router)
