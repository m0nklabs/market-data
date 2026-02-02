"""Market Data Service daemon - main entry point."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import threading
from collections.abc import Iterable
from datetime import datetime, timezone

from market_data.api.main import run_api
from market_data.config import settings
from market_data.exchanges.bitfinex_ws import BitfinexCandleWSClient, CandleSubscription
from market_data.services.backfill import BackfillService
from market_data.services.gap_repair import GapRepairService
from market_data.storage.postgres import PostgresStorage
from market_data.types import Candle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class MarketDataDaemon:
    """Main daemon for market data ingestion."""

    def __init__(self):
        self.storage = PostgresStorage()
        self.backfill_service = BackfillService(self.storage)
        self.gap_repair_service = GapRepairService(self.storage)
        self._running = False
        self._api_thread: threading.Thread | None = None
        self._ws_clients: list[BitfinexCandleWSClient] = []
        self._ws_queue: asyncio.Queue[Candle] | None = None

    def init_database(self) -> None:
        """Initialize database schema."""
        logger.info("Initializing database schema...")
        self.storage.init_schema()
        logger.info("Database schema ready")

    def start_api(self) -> None:
        """Start API server in background thread."""
        logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")
        self._api_thread = threading.Thread(target=run_api, daemon=True)
        self._api_thread.start()

    async def run_backfill(self) -> None:
        """Run initial backfill if configured."""
        if not settings.backfill_on_startup:
            logger.info("Backfill on startup disabled")
            return

        logger.info(f"Starting backfill for {settings.backfill_days} days...")
        
        # Run in thread pool to not block
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            self.backfill_service.backfill_all,
            settings.backfill_days,
        )
        
        total = sum(v for v in results.values() if v > 0)
        logger.info(f"Backfill complete: {total} candles across {len(results)} symbol/timeframes")

    async def run_startup_catchup(self) -> None:
        """Quick REST catch-up window to avoid falling behind on startup."""
        if not settings.ws_ingestion_enabled:
            return
        if settings.ws_catchup_lookback_minutes <= 0:
            return

        logger.info(f"Startup catch-up: last {settings.ws_catchup_lookback_minutes} minutes (REST)")
        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None,
            self.backfill_service.catchup_recent,
            settings.ws_catchup_lookback_minutes,
        )
        total = sum(v for v in results.values() if v > 0)
        logger.info(f"Startup catch-up complete: {total} candles")

    def _ws_subscriptions(self) -> list[CandleSubscription]:
        subs: list[CandleSubscription] = []
        for symbol in settings.bitfinex_symbols_list:
            for timeframe in settings.bitfinex_timeframes_list:
                subs.append(CandleSubscription(symbol=symbol, timeframe=timeframe))
        return subs

    async def run_ws_ingestion(self) -> None:
        """Stream realtime candles from Bitfinex WS and persist them."""
        if not settings.ws_ingestion_enabled:
            logger.info("WebSocket ingestion disabled")
            return

        subs = self._ws_subscriptions()
        if not subs:
            logger.info("No WS subscriptions configured")
            return

        self._ws_queue = asyncio.Queue(maxsize=10000)

        dropped = 0

        async def on_candles(candles: list[Candle]) -> None:
            nonlocal dropped
            if not self._ws_queue:
                return
            for candle in candles:
                try:
                    self._ws_queue.put_nowait(candle)
                except asyncio.QueueFull:
                    dropped += 1
                    if dropped % 1000 == 0:
                        logger.warning(f"WS queue full: dropped {dropped} candles")

        max_per_conn = max(1, int(settings.ws_max_subscriptions_per_connection))
        chunks: list[list[CandleSubscription]] = [
            subs[i : i + max_per_conn] for i in range(0, len(subs), max_per_conn)
        ]

        self._ws_clients = [
            BitfinexCandleWSClient(
                subscriptions=chunk,
                on_candles=on_candles,
                reconnect_initial_backoff=settings.ws_reconnect_initial_backoff,
                reconnect_max_backoff=settings.ws_reconnect_max_backoff,
            )
            for chunk in chunks
        ]

        logger.info(
            f"Starting WS ingestion: {len(subs)} subscriptions across {len(self._ws_clients)} connections "
            f"(max_per_conn={max_per_conn})"
        )

        persist_task = asyncio.create_task(self._run_ws_persist_loop())
        try:
            await asyncio.gather(*(client.run() for client in self._ws_clients))
        finally:
            persist_task.cancel()

    async def _run_ws_persist_loop(self) -> None:
        if not self._ws_queue:
            return

        batch: list[Candle] = []
        batch_size = max(1, settings.ws_save_batch_size)
        flush_seconds = max(0.2, settings.ws_save_flush_seconds)
        loop = asyncio.get_running_loop()

        while self._running:
            try:
                candle = await asyncio.wait_for(self._ws_queue.get(), timeout=flush_seconds)
                batch.append(candle)
                if len(batch) >= batch_size:
                    to_save = batch
                    batch = []
                    await loop.run_in_executor(None, self.storage.save_candles, to_save)
            except TimeoutError:
                if batch:
                    to_save = batch
                    batch = []
                    await loop.run_in_executor(None, self.storage.save_candles, to_save)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WS persist error: {e}")

        if batch:
            try:
                await loop.run_in_executor(None, self.storage.save_candles, batch)
            except Exception as e:
                logger.error(f"Final WS persist flush failed: {e}")

    async def run_gap_repair_loop(self) -> None:
        """Periodic gap detection and repair."""
        interval = settings.gap_repair_interval_minutes * 60
        
        while self._running:
            try:
                logger.info("Running gap detection and repair...")
                
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.gap_repair_service.run_maintenance,
                )
                
                logger.info(
                    f"Gap maintenance complete: "
                    f"{result['new_gaps_detected']} new gaps, "
                    f"{result['gaps_repaired']} repaired, "
                    f"{result['repair_failures']} failures"
                )

            except Exception as e:
                logger.error(f"Gap repair error: {e}")

            # Wait for next interval
            await asyncio.sleep(interval)

    async def run_update_loop(self) -> None:
        """Periodic incremental updates (fetch latest candles)."""
        interval = max(10, int(settings.update_interval_seconds))
        
        while self._running:
            try:
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None,
                    self.backfill_service.update_latest,
                )
                
                total = sum(v for v in results.values() if v > 0)
                if total > 0:
                    logger.debug(f"Updated {total} candles")

            except Exception as e:
                logger.error(f"Update error: {e}")

            await asyncio.sleep(interval)

    async def run_cleanup_loop(self) -> None:
        """Periodic cleanup of old candles based on retention policy."""
        # Run cleanup once per day (first run after 1 hour)
        await asyncio.sleep(3600)
        
        while self._running:
            try:
                logger.info("Running data retention cleanup...")
                
                loop = asyncio.get_event_loop()
                deleted = await loop.run_in_executor(
                    None,
                    self.storage.cleanup_old_candles,
                    settings.retention_days,
                )
                
                total = sum(deleted.values())
                if total > 0:
                    logger.info(f"Cleanup complete: deleted {total} old candles")
                else:
                    logger.info("Cleanup complete: no old candles to delete")

            except Exception as e:
                logger.error(f"Cleanup error: {e}")

            # Run once per day
            await asyncio.sleep(86400)

    async def run(self) -> None:
        """Main daemon loop."""
        self._running = True
        
        logger.info("=" * 50)
        logger.info("Market Data Service Starting")
        logger.info(f"Symbols: {settings.bitfinex_symbols_list}")
        logger.info(f"Timeframes: {settings.bitfinex_timeframes_list}")
        logger.info("=" * 50)

        # Initialize
        self.init_database()
        
        # Start API server
        self.start_api()

        # Start realtime WS ingestion early (prevents new gaps).
        ws_task = asyncio.create_task(self.run_ws_ingestion())

        # Quick startup catch-up (REST) to avoid falling behind while long backfills run.
        catchup_task = asyncio.create_task(self.run_startup_catchup())

        # Run initial backfill (can be long); do not block startup.
        backfill_task = asyncio.create_task(self.run_backfill())
        
        # Start background tasks
        tasks: list[asyncio.Task] = [
            ws_task,
            catchup_task,
            backfill_task,
            asyncio.create_task(self.run_gap_repair_loop()),
            asyncio.create_task(self.run_update_loop()),
            asyncio.create_task(self.run_cleanup_loop()),
        ]
        
        logger.info("Daemon running. Press Ctrl+C to stop.")
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Daemon stopping...")

    def stop(self) -> None:
        """Stop the daemon."""
        self._running = False
        for client in self._ws_clients:
            client.stop()
        logger.info("Stop signal received")


def main():
    """Entry point."""
    daemon = MarketDataDaemon()

    # Handle signals
    def signal_handler(sig, frame):
        daemon.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run
    try:
        asyncio.run(daemon.run())
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == "__main__":
    main()
