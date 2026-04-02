from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.health import router as health_router
from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("POLYPRO backend starting up")
    yield


app = FastAPI(title="POLYPRO", version="0.1.1", lifespan=lifespan)
app.include_router(health_router)
