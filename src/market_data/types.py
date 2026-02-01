"""Core types for market data service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal

Timeframe = Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]


@dataclass
class Candle:
    """OHLCV candle data."""

    exchange: str
    symbol: str
    timeframe: str
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def to_dict(self) -> dict:
        return {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "open_time": self.open_time.isoformat(),
            "close_time": self.close_time.isoformat(),
            "open": str(self.open),
            "high": str(self.high),
            "low": str(self.low),
            "close": str(self.close),
            "volume": str(self.volume),
        }


@dataclass
class CandleGap:
    """Detected gap in candle data."""

    id: int | None
    exchange: str
    symbol: str
    timeframe: str
    gap_start: datetime
    gap_end: datetime
    detected_at: datetime
    repaired_at: datetime | None = None


@dataclass
class IngestionJob:
    """Track ingestion job status."""

    id: int | None
    exchange: str
    symbol: str
    timeframe: str
    job_type: Literal["backfill", "realtime", "gap_repair"]
    status: Literal["running", "success", "failed"]
    started_at: datetime
    completed_at: datetime | None = None
    candles_fetched: int = 0
    last_error: str | None = None
