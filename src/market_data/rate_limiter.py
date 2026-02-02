"""Global rate limiter for Bitfinex API.

Singleton pattern ensures all tasks share the same rate limiter,
preventing multiple parallel requests from exceeding API limits.

Bitfinex limits (https://docs.bitfinex.com/docs/requirements-and-limitations):
- REST API: 10-90 requests per minute depending on endpoint
- If rate limited: IP blocked for 60 seconds
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class GlobalRateLimiter:
    """Thread-safe global rate limiter for API requests.
    
    Uses a simple token bucket algorithm with configurable delay between requests.
    All threads/tasks share the same limiter instance.
    """
    
    _instance: GlobalRateLimiter | None = None
    _lock = threading.Lock()
    
    def __new__(cls) -> GlobalRateLimiter:
        """Singleton pattern - return existing instance or create new one."""
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize rate limiter (only runs once due to singleton)."""
        if getattr(self, "_initialized", False):
            return
            
        from market_data.config import settings
        
        self._request_lock = threading.Lock()
        self._last_request_time: float = 0
        self._consecutive_rate_limits: int = 0
        
        # Load settings
        self.request_delay = settings.rate_limit_delay
        self.max_retries = settings.rate_limit_max_retries
        self.initial_backoff = settings.rate_limit_initial_backoff
        self.max_backoff = settings.rate_limit_max_backoff
        self.min_backoff_on_429 = settings.rate_limit_min_backoff_seconds
        
        self._initialized = True
        logger.info(
            f"Global rate limiter initialized: {1/self.request_delay:.1f} req/s max, "
            f"{self.max_retries} retries, backoff {self.initial_backoff}-{self.max_backoff}s"
        )
    
    def wait_for_slot(self) -> None:
        """Wait until a request slot is available.
        
        Thread-safe - only one thread can make a request at a time.
        """
        with self._request_lock:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.request_delay:
                sleep_time = self.request_delay - elapsed
                time.sleep(sleep_time)
            self._last_request_time = time.time()
    
    def record_success(self) -> None:
        """Record a successful request - gradually reduce backoff."""
        with self._request_lock:
            self._consecutive_rate_limits = max(0, self._consecutive_rate_limits - 1)
    
    def record_rate_limit(self) -> float:
        """Record a rate limit (429) response.
        
        Returns the recommended backoff time in seconds.
        """
        with self._request_lock:
            self._consecutive_rate_limits += 1
            # Exponential backoff based on consecutive failures
            backoff = self.initial_backoff * (2 ** min(self._consecutive_rate_limits, 6))
            backoff = min(backoff, self.max_backoff)
            return max(self.min_backoff_on_429, backoff)
    
    def get_stats(self) -> dict[str, Any]:
        """Get current rate limiter statistics."""
        return {
            "request_delay": self.request_delay,
            "requests_per_minute": 60 / self.request_delay,
            "consecutive_rate_limits": self._consecutive_rate_limits,
            "last_request_time": self._last_request_time,
        }


# Global instance for easy access
_rate_limiter: GlobalRateLimiter | None = None


def get_rate_limiter() -> GlobalRateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = GlobalRateLimiter()
    return _rate_limiter
