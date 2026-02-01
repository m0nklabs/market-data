"""Backfill service for historical candle data."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from market_data.config import settings
from market_data.exchanges.base import ExchangeAdapter
from market_data.exchanges.bitfinex import BitfinexAdapter
from market_data.storage.postgres import PostgresStorage
from market_data.types import IngestionJob

logger = logging.getLogger(__name__)


class BackfillService:
    """Service for backfilling historical candle data."""

    def __init__(
        self,
        storage: PostgresStorage | None = None,
        exchange: ExchangeAdapter | None = None,
    ):
        self.storage = storage or PostgresStorage()
        self.exchange = exchange or BitfinexAdapter()

    def backfill_symbol(
        self,
        symbol: str,
        timeframe: str,
        days: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> int:
        """Backfill candles for a single symbol/timeframe.
        
        Returns total candles saved.
        """
        days = days or settings.backfill_days
        end = end or datetime.now(timezone.utc)
        
        # Check if we have existing data - resume from there
        latest = self.storage.get_latest_candle_time("bitfinex", symbol, timeframe)
        if latest and not start:
            # Ensure timezone awareness for comparison
            if latest.tzinfo is None:
                latest = latest.replace(tzinfo=timezone.utc)
            start = latest
            logger.info(f"Resuming backfill from {start} for {symbol}/{timeframe}")
        elif not start:
            start = end - timedelta(days=days)
        
        # Ensure start has timezone
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)

        # Create job record
        job = IngestionJob(
            id=None,
            exchange="bitfinex",
            symbol=symbol,
            timeframe=timeframe,
            job_type="backfill",
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        job_id = self.storage.create_job(job)

        try:
            logger.info(f"Backfilling {symbol}/{timeframe} from {start} to {end}")
            
            candles = self.exchange.fetch_candles(symbol, timeframe, start, end)
            
            if candles:
                saved = self.storage.save_candles(candles)
                logger.info(f"Saved {saved} candles for {symbol}/{timeframe}")
                
                self.storage.update_job(
                    job_id,
                    status="success",
                    candles_fetched=saved,
                    completed=True,
                )
                return saved
            else:
                logger.warning(f"No candles returned for {symbol}/{timeframe}")
                self.storage.update_job(
                    job_id,
                    status="success",
                    candles_fetched=0,
                    completed=True,
                )
                return 0

        except Exception as e:
            logger.error(f"Backfill failed for {symbol}/{timeframe}: {e}")
            self.storage.update_job(
                job_id,
                status="failed",
                last_error=str(e),
                completed=True,
            )
            raise

    def backfill_all(self, days: int | None = None) -> dict[str, int]:
        """Backfill all configured symbols/timeframes.
        
        Returns dict of symbol/timeframe -> candle count.
        """
        results = {}
        
        for symbol in settings.bitfinex_symbols_list:
            for timeframe in settings.bitfinex_timeframes_list:
                key = f"{symbol}/{timeframe}"
                try:
                    count = self.backfill_symbol(symbol, timeframe, days=days)
                    results[key] = count
                except Exception as e:
                    logger.error(f"Failed to backfill {key}: {e}")
                    results[key] = -1

        return results

    def update_latest(self) -> dict[str, int]:
        """Fetch latest candles for all symbols (incremental update).
        
        Returns dict of symbol/timeframe -> new candle count.
        """
        results = {}

        for symbol in settings.bitfinex_symbols_list:
            for timeframe in settings.bitfinex_timeframes_list:
                key = f"{symbol}/{timeframe}"
                try:
                    # Get latest 10 candles to catch up
                    candles = self.exchange.fetch_latest_candles(symbol, timeframe, limit=10)
                    if candles:
                        saved = self.storage.save_candles(candles)
                        results[key] = saved
                        logger.debug(f"Updated {saved} candles for {key}")
                    else:
                        results[key] = 0
                except Exception as e:
                    logger.error(f"Failed to update {key}: {e}")
                    results[key] = -1

        return results
