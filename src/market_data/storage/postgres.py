"""PostgreSQL storage implementation."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from market_data.config import settings
from market_data.types import Candle, CandleGap, IngestionJob

logger = logging.getLogger(__name__)


class PostgresStorage:
    """PostgreSQL storage for candle data."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.database_url
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                self.database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
            )
        return self._engine

    def init_schema(self) -> None:
        """Initialize database schema."""
        schema_path = Path(__file__).parent / "schema.sql"
        schema_sql = schema_path.read_text()

        with self.engine.connect() as conn:
            conn.execute(text(schema_sql))
            conn.commit()
        logger.info("Database schema initialized")

    def save_candles(self, candles: list[Candle]) -> int:
        """Upsert candles to database. Returns count saved."""
        if not candles:
            return 0

        sql = text("""
            INSERT INTO candles (exchange, symbol, timeframe, open_time, close_time, open, high, low, close, volume)
            VALUES (:exchange, :symbol, :timeframe, :open_time, :close_time, :open, :high, :low, :close, :volume)
            ON CONFLICT (exchange, symbol, timeframe, open_time) 
            DO UPDATE SET
                close_time = EXCLUDED.close_time,
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
        """)

        with self.engine.connect() as conn:
            for candle in candles:
                conn.execute(sql, {
                    "exchange": candle.exchange,
                    "symbol": candle.symbol,
                    "timeframe": candle.timeframe,
                    "open_time": candle.open_time,
                    "close_time": candle.close_time,
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "volume": candle.volume,
                })
            conn.commit()

        return len(candles)

    def get_candles(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 1000,
    ) -> list[Candle]:
        """Retrieve candles from database."""
        conditions = ["exchange = :exchange", "symbol = :symbol", "timeframe = :timeframe"]
        params: dict = {"exchange": exchange, "symbol": symbol, "timeframe": timeframe, "limit": limit}

        if start:
            conditions.append("open_time >= :start")
            params["start"] = start
        if end:
            conditions.append("open_time < :end")
            params["end"] = end

        sql = text(f"""
            SELECT exchange, symbol, timeframe, open_time, close_time, open, high, low, close, volume
            FROM candles
            WHERE {" AND ".join(conditions)}
            ORDER BY open_time DESC
            LIMIT :limit
        """)

        with self.engine.connect() as conn:
            result = conn.execute(sql, params)
            rows = result.fetchall()

        candles = [
            Candle(
                exchange=row[0],
                symbol=row[1],
                timeframe=row[2],
                open_time=row[3],
                close_time=row[4],
                open=row[5],
                high=row[6],
                low=row[7],
                close=row[8],
                volume=row[9],
            )
            for row in rows
        ]
        candles.reverse()  # Return in chronological order
        return candles

    def get_latest_candle_time(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
    ) -> datetime | None:
        """Get the most recent candle time for a symbol/timeframe."""
        sql = text("""
            SELECT MAX(open_time) FROM candles
            WHERE exchange = :exchange AND symbol = :symbol AND timeframe = :timeframe
        """)

        with self.engine.connect() as conn:
            result = conn.execute(sql, {"exchange": exchange, "symbol": symbol, "timeframe": timeframe})
            row = result.fetchone()

        return row[0] if row and row[0] else None

    def get_candle_count(
        self,
        exchange: str,
        symbol: str,
        timeframe: str,
    ) -> int:
        """Get total candle count for symbol/timeframe."""
        sql = text("""
            SELECT COUNT(*) FROM candles
            WHERE exchange = :exchange AND symbol = :symbol AND timeframe = :timeframe
        """)

        with self.engine.connect() as conn:
            result = conn.execute(sql, {"exchange": exchange, "symbol": symbol, "timeframe": timeframe})
            row = result.fetchone()

        return row[0] if row else 0

    # Gap management
    def save_gap(self, gap: CandleGap) -> int:
        """Save detected gap. Returns gap ID."""
        sql = text("""
            INSERT INTO candle_gaps (exchange, symbol, timeframe, gap_start, gap_end, detected_at)
            VALUES (:exchange, :symbol, :timeframe, :gap_start, :gap_end, :detected_at)
            ON CONFLICT (exchange, symbol, timeframe, gap_start, gap_end) DO NOTHING
            RETURNING id
        """)

        with self.engine.connect() as conn:
            result = conn.execute(sql, {
                "exchange": gap.exchange,
                "symbol": gap.symbol,
                "timeframe": gap.timeframe,
                "gap_start": gap.gap_start,
                "gap_end": gap.gap_end,
                "detected_at": gap.detected_at,
            })
            conn.commit()
            row = result.fetchone()
            return row[0] if row else 0

    def get_unrepaired_gaps(
        self,
        exchange: str | None = None,
        symbol: str | None = None,
        timeframe: str | None = None,
    ) -> list[CandleGap]:
        """Get gaps that haven't been repaired."""
        conditions = ["repaired_at IS NULL"]
        params: dict = {}

        if exchange:
            conditions.append("exchange = :exchange")
            params["exchange"] = exchange
        if symbol:
            conditions.append("symbol = :symbol")
            params["symbol"] = symbol
        if timeframe:
            conditions.append("timeframe = :timeframe")
            params["timeframe"] = timeframe

        sql = text(f"""
            SELECT id, exchange, symbol, timeframe, gap_start, gap_end, detected_at, repaired_at
            FROM candle_gaps
            WHERE {" AND ".join(conditions)}
            ORDER BY gap_start ASC
        """)

        with self.engine.connect() as conn:
            result = conn.execute(sql, params)
            rows = result.fetchall()

        return [
            CandleGap(
                id=row[0],
                exchange=row[1],
                symbol=row[2],
                timeframe=row[3],
                gap_start=row[4],
                gap_end=row[5],
                detected_at=row[6],
                repaired_at=row[7],
            )
            for row in rows
        ]

    def mark_gap_repaired(self, gap_id: int) -> None:
        """Mark a gap as repaired."""
        sql = text("""
            UPDATE candle_gaps SET repaired_at = :now WHERE id = :id
        """)

        with self.engine.connect() as conn:
            conn.execute(sql, {"id": gap_id, "now": datetime.now(timezone.utc)})
            conn.commit()

    # Job tracking
    def create_job(self, job: IngestionJob) -> int:
        """Create new ingestion job. Returns job ID."""
        sql = text("""
            INSERT INTO ingestion_jobs (exchange, symbol, timeframe, job_type, status, started_at)
            VALUES (:exchange, :symbol, :timeframe, :job_type, :status, :started_at)
            RETURNING id
        """)

        with self.engine.connect() as conn:
            result = conn.execute(sql, {
                "exchange": job.exchange,
                "symbol": job.symbol,
                "timeframe": job.timeframe,
                "job_type": job.job_type,
                "status": job.status,
                "started_at": job.started_at,
            })
            conn.commit()
            row = result.fetchone()
            return row[0] if row else 0

    def update_job(
        self,
        job_id: int,
        status: str | None = None,
        candles_fetched: int | None = None,
        last_error: str | None = None,
        completed: bool = False,
    ) -> None:
        """Update job status."""
        updates = []
        params: dict = {"id": job_id}

        if status:
            updates.append("status = :status")
            params["status"] = status
        if candles_fetched is not None:
            updates.append("candles_fetched = :candles_fetched")
            params["candles_fetched"] = candles_fetched
        if last_error:
            updates.append("last_error = :last_error")
            params["last_error"] = last_error
        if completed:
            updates.append("completed_at = :completed_at")
            params["completed_at"] = datetime.now(timezone.utc)

        if not updates:
            return

        sql = text(f"UPDATE ingestion_jobs SET {', '.join(updates)} WHERE id = :id")

        with self.engine.connect() as conn:
            conn.execute(sql, params)
            conn.commit()

    def get_recent_jobs(self, limit: int = 20) -> list[IngestionJob]:
        """Get recent ingestion jobs."""
        sql = text("""
            SELECT id, exchange, symbol, timeframe, job_type, status, started_at, completed_at, candles_fetched, last_error
            FROM ingestion_jobs
            ORDER BY started_at DESC
            LIMIT :limit
        """)

        with self.engine.connect() as conn:
            result = conn.execute(sql, {"limit": limit})
            rows = result.fetchall()

        return [
            IngestionJob(
                id=row[0],
                exchange=row[1],
                symbol=row[2],
                timeframe=row[3],
                job_type=row[4],
                status=row[5],
                started_at=row[6],
                completed_at=row[7],
                candles_fetched=row[8],
                last_error=row[9],
            )
            for row in rows
        ]

    def get_ingestion_status(self) -> dict:
        """Get overall ingestion status summary."""
        sql = text("""
            SELECT 
                exchange,
                symbol,
                timeframe,
                COUNT(*) as candle_count,
                MIN(open_time) as oldest,
                MAX(open_time) as newest
            FROM candles
            GROUP BY exchange, symbol, timeframe
            ORDER BY exchange, symbol, timeframe
        """)

        with self.engine.connect() as conn:
            result = conn.execute(sql)
            rows = result.fetchall()

        return {
            "symbols": [
                {
                    "exchange": row[0],
                    "symbol": row[1],
                    "timeframe": row[2],
                    "candle_count": row[3],
                    "oldest": row[4].isoformat() if row[4] else None,
                    "newest": row[5].isoformat() if row[5] else None,
                }
                for row in rows
            ]
        }
