"""Candle data routes."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from market_data.storage.postgres import PostgresStorage

router = APIRouter()


@router.get("")
def get_candles(
    exchange: Annotated[str, Query(description="Exchange name")] = "bitfinex",
    symbol: Annotated[str, Query(description="Trading pair symbol")] = "BTCUSD",
    timeframe: Annotated[str, Query(description="Candle timeframe")] = "1h",
    start: Annotated[datetime | None, Query(description="Start time (ISO 8601)")] = None,
    end: Annotated[datetime | None, Query(description="End time (ISO 8601)")] = None,
    limit: Annotated[int, Query(description="Max candles to return", ge=1, le=10000)] = 1000,
):
    """Get candles for a symbol/timeframe."""
    storage = PostgresStorage()
    
    candles = storage.get_candles(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=limit,
    )

    return {
        "exchange": exchange,
        "symbol": symbol,
        "timeframe": timeframe,
        "count": len(candles),
        "candles": [candle.to_dict() for candle in candles],
    }


@router.get("/latest")
def get_latest_candles(
    exchange: Annotated[str, Query(description="Exchange name")] = "bitfinex",
    symbol: Annotated[str, Query(description="Trading pair symbol")] = "BTCUSD",
    timeframe: Annotated[str, Query(description="Candle timeframe")] = "1h",
    limit: Annotated[int, Query(description="Number of candles", ge=1, le=1000)] = 100,
):
    """Get the N most recent candles."""
    storage = PostgresStorage()
    
    candles = storage.get_candles(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
    )

    return {
        "exchange": exchange,
        "symbol": symbol,
        "timeframe": timeframe,
        "count": len(candles),
        "candles": [candle.to_dict() for candle in candles],
    }


@router.get("/count")
def get_candle_count(
    exchange: Annotated[str, Query(description="Exchange name")] = "bitfinex",
    symbol: Annotated[str, Query(description="Trading pair symbol")] = "BTCUSD",
    timeframe: Annotated[str, Query(description="Candle timeframe")] = "1h",
):
    """Get total candle count for a symbol/timeframe."""
    storage = PostgresStorage()
    
    count = storage.get_candle_count(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
    )

    return {
        "exchange": exchange,
        "symbol": symbol,
        "timeframe": timeframe,
        "count": count,
    }


@router.get("/symbols")
def list_symbols():
    """List all symbols with data."""
    storage = PostgresStorage()
    status = storage.get_ingestion_status()
    
    # Extract unique symbols
    symbols = list(set(s["symbol"] for s in status.get("symbols", [])))
    symbols.sort()
    
    return {"symbols": symbols}
