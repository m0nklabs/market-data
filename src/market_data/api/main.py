"""FastAPI application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from market_data.api.routes.candles import router as candles_router
from market_data.api.routes.status import router as status_router
from market_data.config import settings
from market_data.storage.postgres import PostgresStorage

logger = logging.getLogger(__name__)

storage: PostgresStorage | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    global storage
    storage = PostgresStorage()
    logger.info("Market Data API starting up")
    yield
    logger.info("Market Data API shutting down")


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Market Data Service",
        description="REST API for crypto OHLCV candle data",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(status_router, tags=["status"])
    app.include_router(candles_router, prefix="/candles", tags=["candles"])

    return app


app = create_app()


def run_api():
    """Run the API server."""
    import uvicorn

    uvicorn.run(
        "market_data.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )
