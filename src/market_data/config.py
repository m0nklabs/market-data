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
    backfill_days: int = Field(
        default=365,
        description="Days of historical data to backfill",
    )
    gap_repair_interval_minutes: int = Field(
        default=60,
        description="Interval between gap repair runs",
    )
    health_check_interval_seconds: int = Field(
        default=30,
        description="Interval between health checks",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def bitfinex_symbols_list(self) -> list[str]:
        return [s.strip() for s in self.bitfinex_symbols.split(",")]

    @property
    def bitfinex_timeframes_list(self) -> list[str]:
        return [t.strip() for t in self.bitfinex_timeframes.split(",")]


settings = Settings()
