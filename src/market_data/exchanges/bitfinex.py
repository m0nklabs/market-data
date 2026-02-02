"""Bitfinex exchange adapter."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Callable

import httpx

from market_data.exchanges.base import ExchangeAdapter
from market_data.types import Candle

logger = logging.getLogger(__name__)

# Timeframe to API string and delta
TIMEFRAMES = {
    "1m": ("1m", timedelta(minutes=1)),
    "5m": ("5m", timedelta(minutes=5)),
    "15m": ("15m", timedelta(minutes=15)),
    "30m": ("30m", timedelta(minutes=30)),
    "1h": ("1h", timedelta(hours=1)),
    "4h": ("4h", timedelta(hours=4)),
    "1d": ("1D", timedelta(days=1)),
    "1w": ("1W", timedelta(weeks=1)),
}

BASE_URL = "https://api-pub.bitfinex.com/v2"


class BitfinexAdapter(ExchangeAdapter):
    """Bitfinex REST API adapter for candle data.
    
    Rate Limits (from Bitfinex docs - https://docs.bitfinex.com/docs/requirements-and-limitations):
    - REST API: 10-90 requests per minute depending on endpoint
    - If rate limited: IP blocked for 60 seconds
    - No difference between public/authenticated for rate limits
    
    Uses GLOBAL rate limiter shared across all instances/threads.
    """

    def __init__(self):
        # Import here to avoid circular imports
        from market_data.config import settings
        from market_data.rate_limiter import get_rate_limiter
        
        self._rate_limiter = get_rate_limiter()
        self._client = httpx.Client(timeout=30.0)
        
        # Keep local copies for retry logic
        self.max_retries = settings.rate_limit_max_retries
        self.max_backoff = settings.rate_limit_max_backoff

    def _api_timeframe(self, timeframe: str) -> str:
        """Convert timeframe to API format."""
        return TIMEFRAMES.get(timeframe, (timeframe, timedelta(hours=1)))[0]

    def _timeframe_delta(self, timeframe: str) -> timedelta:
        """Get timedelta for timeframe."""
        return TIMEFRAMES.get(timeframe, ("1h", timedelta(hours=1)))[1]

    def _request_with_retry(self, url: str, params: dict[str, Any] | None = None) -> Any:
        """Make request with global rate limiting and exponential backoff retry.
        
        Uses GLOBAL rate limiter to coordinate across all threads/tasks.
        """
        for attempt in range(self.max_retries):
            # Wait for rate limit slot (thread-safe, global)
            self._rate_limiter.wait_for_slot()
            
            try:
                response = self._client.get(url, params=params)
                
                if response.status_code == 429:
                    # Rate limited - record and back off
                    backoff = self._rate_limiter.record_rate_limit()
                    stats = self._rate_limiter.get_stats()
                    logger.warning(
                        f"Rate limited (429), backing off {backoff:.0f}s "
                        f"(attempt {attempt + 1}/{self.max_retries}, "
                        f"consecutive: {stats['consecutive_rate_limits']})"
                    )
                    time.sleep(backoff)
                    continue

                # Success - record it
                self._rate_limiter.record_success()
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"HTTP error {e.response.status_code}, retry {attempt + 1}")
                time.sleep(2.0)

            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Request error: {e}, retry {attempt + 1}")
                time.sleep(2.0)

        # After max retries, log and return None instead of raising
        logger.error(f"Failed after {self.max_retries} retries, will retry later")
        return None

    def _parse_candle(
        self,
        data: list,
        exchange: str,
        symbol: str,
        timeframe: str,
    ) -> Candle:
        """Parse API response to Candle object."""
        # API returns: [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
        ts_ms, open_, close_, high_, low_, volume = data
        open_time = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        close_time = open_time + self._timeframe_delta(timeframe)

        return Candle(
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe,
            open_time=open_time,
            close_time=close_time,
            open=Decimal(str(open_)),
            high=Decimal(str(high_)),
            low=Decimal(str(low_)),
            close=Decimal(str(close_)),
            volume=Decimal(str(abs(volume))),
        )

    def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        """Fetch historical candles between start and end."""
        api_tf = self._api_timeframe(timeframe)
        api_symbol = f"t{symbol}" if not symbol.startswith("t") else symbol

        # Bitfinex API returns max 10000 candles per request
        all_candles: list[Candle] = []
        current_start = start

        while current_start < end:
            url = f"{BASE_URL}/candles/trade:{api_tf}:{api_symbol}/hist"
            params = {
                "start": int(current_start.timestamp() * 1000),
                "end": int(end.timestamp() * 1000),
                "limit": 10000,
                "sort": 1,  # oldest first
            }

            data = self._request_with_retry(url, params)

            if not data:
                break

            for item in data:
                candle = self._parse_candle(item, "bitfinex", symbol, timeframe)
                all_candles.append(candle)

            # Move start to after last candle
            if all_candles:
                current_start = all_candles[-1].close_time
            else:
                break

            # Small delay between paginated requests (in addition to base throttle)
            time.sleep(0.2)

        return all_candles

    def fetch_latest_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[Candle]:
        """Fetch most recent candles."""
        api_tf = self._api_timeframe(timeframe)
        api_symbol = f"t{symbol}" if not symbol.startswith("t") else symbol

        url = f"{BASE_URL}/candles/trade:{api_tf}:{api_symbol}/hist"
        params = {"limit": limit, "sort": -1}  # newest first

        data = self._request_with_retry(url, params)
        
        if not data:
            return []

        candles = [
            self._parse_candle(item, "bitfinex", symbol, timeframe)
            for item in data
        ]

        # Return in chronological order
        candles.reverse()
        return candles

    def subscribe_candles(
        self,
        symbol: str,
        timeframe: str,
        callback: Callable[[Candle], None],
    ) -> None:
        """Subscribe to realtime candle updates (not implemented yet)."""
        raise NotImplementedError("WebSocket streaming not yet implemented")

    def get_symbols(self) -> list[str]:
        """List available trading pairs."""
        url = f"{BASE_URL}/conf/pub:list:pair:exchange"
        data = self._request_with_retry(url)
        return data[0] if data else []
