"""Base exchange adapter protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable

from market_data.types import Candle


class ExchangeAdapter(ABC):
    """Protocol for exchange data sources."""

    @abstractmethod
    def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        """Fetch historical candles."""
        ...

    @abstractmethod
    def fetch_latest_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[Candle]:
        """Fetch most recent candles."""
        ...

    @abstractmethod
    def subscribe_candles(
        self,
        symbol: str,
        timeframe: str,
        callback: Callable[[Candle], None],
    ) -> None:
        """Subscribe to realtime candle updates."""
        ...

    @abstractmethod
    def get_symbols(self) -> list[str]:
        """List available trading pairs."""
        ...
