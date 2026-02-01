"""Gap detection and repair service."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from market_data.config import settings
from market_data.exchanges.base import ExchangeAdapter
from market_data.exchanges.bitfinex import BitfinexAdapter, TIMEFRAMES
from market_data.storage.postgres import PostgresStorage
from market_data.types import CandleGap, IngestionJob

logger = logging.getLogger(__name__)


class GapRepairService:
    """Service for detecting and repairing gaps in candle data."""

    def __init__(
        self,
        storage: PostgresStorage | None = None,
        exchange: ExchangeAdapter | None = None,
    ):
        self.storage = storage or PostgresStorage()
        self.exchange = exchange or BitfinexAdapter()

    def _get_timeframe_delta(self, timeframe: str) -> timedelta:
        """Get expected delta between candles."""
        return TIMEFRAMES.get(timeframe, ("1h", timedelta(hours=1)))[1]

    def detect_gaps(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[CandleGap]:
        """Detect gaps in candle data.
        
        A gap is detected when the time between consecutive candles
        is greater than the expected timeframe delta.
        """
        end = end or datetime.now(timezone.utc)
        start = start or (end - timedelta(days=30))

        candles = self.storage.get_candles(
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=100000,  # Get all in range
        )

        if len(candles) < 2:
            return []

        expected_delta = self._get_timeframe_delta(timeframe)
        # Allow some tolerance (5% of timeframe)
        tolerance = expected_delta * 0.05
        gaps = []

        for i in range(len(candles) - 1):
            current = candles[i]
            next_candle = candles[i + 1]

            actual_delta = next_candle.open_time - current.close_time

            # If gap is larger than expected (with tolerance)
            if actual_delta > expected_delta + tolerance:
                gap = CandleGap(
                    id=None,
                    exchange=exchange,
                    symbol=symbol,
                    timeframe=timeframe,
                    gap_start=current.close_time,
                    gap_end=next_candle.open_time,
                    detected_at=datetime.now(timezone.utc),
                )
                gaps.append(gap)
                logger.info(
                    f"Gap detected: {symbol}/{timeframe} "
                    f"from {gap.gap_start} to {gap.gap_end} "
                    f"({actual_delta})"
                )

        return gaps

    def detect_and_save_gaps(
        self,
        exchange: str | None = None,
        symbol: str | None = None,
        timeframe: str | None = None,
    ) -> int:
        """Detect gaps for configured symbols and save to database.
        
        Returns count of new gaps detected.
        """
        symbols = [symbol] if symbol else settings.bitfinex_symbols_list
        timeframes = [timeframe] if timeframe else settings.bitfinex_timeframes_list
        exchange = exchange or "bitfinex"

        total_gaps = 0

        for sym in symbols:
            for tf in timeframes:
                gaps = self.detect_gaps(exchange, sym, tf)
                for gap in gaps:
                    gap_id = self.storage.save_gap(gap)
                    if gap_id:
                        total_gaps += 1

        logger.info(f"Detected {total_gaps} new gaps")
        return total_gaps

    def repair_gap(self, gap: CandleGap) -> int:
        """Repair a single gap by fetching missing candles.
        
        Returns count of candles fetched.
        """
        # Create job record
        job = IngestionJob(
            id=None,
            exchange=gap.exchange,
            symbol=gap.symbol,
            timeframe=gap.timeframe,
            job_type="gap_repair",
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        job_id = self.storage.create_job(job)

        try:
            logger.info(
                f"Repairing gap: {gap.symbol}/{gap.timeframe} "
                f"from {gap.gap_start} to {gap.gap_end}"
            )

            # Ensure timezone awareness for gap times from DB
            gap_start = gap.gap_start
            gap_end = gap.gap_end
            if gap_start.tzinfo is None:
                gap_start = gap_start.replace(tzinfo=timezone.utc)
            if gap_end.tzinfo is None:
                gap_end = gap_end.replace(tzinfo=timezone.utc)

            candles = self.exchange.fetch_candles(
                gap.symbol,
                gap.timeframe,
                gap_start,
                gap_end,
            )

            if candles:
                saved = self.storage.save_candles(candles)
                logger.info(f"Repaired gap with {saved} candles")
            else:
                saved = 0
                logger.warning(f"No candles returned for gap repair")

            # Mark gap as repaired
            if gap.id:
                self.storage.mark_gap_repaired(gap.id)

            self.storage.update_job(
                job_id,
                status="success",
                candles_fetched=saved,
                completed=True,
            )
            return saved

        except Exception as e:
            logger.error(f"Gap repair failed: {e}")
            self.storage.update_job(
                job_id,
                status="failed",
                last_error=str(e),
                completed=True,
            )
            raise

    def repair_all_gaps(self) -> dict[str, int]:
        """Repair all unrepaired gaps.
        
        Returns dict of gap_id -> candles fetched.
        """
        gaps = self.storage.get_unrepaired_gaps()
        results = {}

        for gap in gaps:
            try:
                count = self.repair_gap(gap)
                results[f"gap_{gap.id}"] = count
            except Exception as e:
                logger.error(f"Failed to repair gap {gap.id}: {e}")
                results[f"gap_{gap.id}"] = -1

        return results

    def run_maintenance(self) -> dict:
        """Run full gap detection and repair cycle.
        
        Returns summary of actions taken.
        """
        # First detect new gaps
        new_gaps = self.detect_and_save_gaps()

        # Then repair all unrepaired gaps
        repairs = self.repair_all_gaps()

        return {
            "new_gaps_detected": new_gaps,
            "gaps_repaired": len([v for v in repairs.values() if v >= 0]),
            "repair_failures": len([v for v in repairs.values() if v < 0]),
        }
