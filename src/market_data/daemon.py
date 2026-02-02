"""Market Data Service daemon - main entry point."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import threading
from datetime import datetime, timezone

from market_data.api.main import run_api
from market_data.config import settings
from market_data.services.backfill import BackfillService
from market_data.services.gap_repair import GapRepairService
from market_data.storage.postgres import PostgresStorage

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
        # Update every minute
        interval = 60
        
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
        
        # Run initial backfill
        await self.run_backfill()
        
        # Start background tasks
        tasks = [
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
