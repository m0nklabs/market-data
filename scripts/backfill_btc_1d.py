#!/usr/bin/env python3
"""Quick backfill script for BTCUSD 1d candles."""

import asyncio
import sys
sys.path.insert(0, "/home/flip/market-data/src")

from datetime import datetime, timedelta, timezone
from market_data.services.backfill import BackfillService


def main():
    service = BackfillService()
    
    # Backfill BTCUSD 1d for 365 days
    symbol = "BTCUSD"
    timeframe = "1d"
    days = 365
    
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    
    print(f"Backfilling {symbol}/{timeframe} from {start} to {end}...")
    
    count = service.backfill_symbol(symbol, timeframe, start=start, end=end)
    print(f"✅ Saved {count} candles")


if __name__ == "__main__":
    main()
