"""Configuration for market data service."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Database
    database_url: str = Field(
        default="postgresql://marketdata:marketdata@localhost:5432/marketdata",
        description="PostgreSQL connection URL",
    )

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8100, description="API port")

    # Bitfinex
    bitfinex_symbols: str = Field(
        default="BTCUSD,ETHUSD",
        description="Symbols to ingest from Bitfinex (comma-separated)",
    )
    bitfinex_timeframes: str = Field(
        default="1h,1d",
        description="Timeframes to ingest (comma-separated)",
    )

    # Daemon
    backfill_on_startup: bool = Field(
        default=True,
        description="Run backfill on daemon startup",
    )
    rest_update_enabled: bool = Field(
        default=False,
        description=(
            "Enable periodic REST update_latest loop. When WS ingestion is enabled, this is usually redundant and can "
            "cause 429s due to high request volume."
        ),
    )
    backfill_days: int = Field(
        default=365,
        description="Days of historical data to backfill",
    )
    gap_repair_max_repairs_per_run: int = Field(
        default=10,
        description="Maximum number of gaps to repair per maintenance cycle (0 = unlimited)",
    )
    gap_detection_interval_minutes: int = Field(
        default=60,
        description="Interval between expensive gap detection scans (minutes)",
    )
    gap_repair_interval_minutes: int = Field(
        default=60,
        description="Interval between gap repair runs",
    )
    update_interval_seconds: int = Field(
        default=60,
        description="Interval between incremental update runs (REST latest candles)",
    )
    health_check_interval_seconds: int = Field(
        default=30,
        description="Interval between health checks",
    )

    # Realtime WebSocket ingestion
    ws_ingestion_enabled: bool = Field(
        default=True,
        description="Enable Bitfinex public WebSocket candle ingestion to prevent new gaps",
    )
    ws_catchup_lookback_minutes: int = Field(
        default=180,
        description="On startup, fetch last N minutes of candles via REST (per symbol/timeframe) to catch up",
    )
    ws_reconnect_initial_backoff: float = Field(
        default=1.0,
        description="Initial reconnect backoff seconds for WebSocket",
    )
    ws_reconnect_max_backoff: float = Field(
        default=60.0,
        description="Maximum reconnect backoff seconds for WebSocket",
    )
    ws_save_batch_size: int = Field(
        default=200,
        description="Batch size when persisting realtime candles",
    )
    ws_save_flush_seconds: float = Field(
        default=2.0,
        description="Flush interval for persisting realtime candles",
    )
    ws_max_subscriptions_per_connection: int = Field(
        default=25,
        description=(
            "Max candle subscriptions per single WebSocket connection. "
            "Bitfinex enforces a subscribe limit; sharding across multiple connections avoids this."
        ),
    )

    # Rate limiting (Bitfinex: 10-90 req/min depending on endpoint; candles can be low)
    rate_limit_delay: float = Field(
        default=6.0,
        description="Seconds between API requests (6.0 ≈ 10 req/min; safer default for candles endpoints)",
    )
    rate_limit_max_retries: int = Field(
        default=10,
        description="Max retries on rate limit (429) errors",
    )
    rate_limit_initial_backoff: float = Field(
        default=2.0,
        description="Initial backoff seconds on 429 error",
    )
    rate_limit_min_backoff_seconds: float = Field(
        default=60.0,
        description="Minimum backoff seconds after a 429 (Bitfinex can block IP for ~60s)",
    )
    rate_limit_max_backoff: float = Field(
        default=120.0,
        description="Maximum backoff seconds",
    )

    # Data retention (days per timeframe)
    retention_1m: int = Field(default=30, description="Days to keep 1m candles")
    retention_1h: int = Field(default=365, description="Days to keep 1h candles")
    retention_4h: int = Field(default=730, description="Days to keep 4h candles")
    retention_1d: int = Field(default=1825, description="Days to keep 1d candles")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def bitfinex_symbols_list(self) -> list[str]:
        return [s.strip() for s in self.bitfinex_symbols.split(",")]

    @property
    def bitfinex_timeframes_list(self) -> list[str]:
        return [t.strip() for t in self.bitfinex_timeframes.split(",")]

    @property
    def retention_days(self) -> dict[str, int]:
        """Get retention days per timeframe."""
        return {
            "1m": self.retention_1m,
            "1h": self.retention_1h,
            "4h": self.retention_4h,
            "1d": self.retention_1d,
        }


settings = Settings()
