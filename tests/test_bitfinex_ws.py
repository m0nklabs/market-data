from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from market_data.exchanges.bitfinex_ws import build_candles_key, parse_ws_candle


def test_build_candles_key() -> None:
    assert build_candles_key("BTCUSD", "1m") == "trade:1m:tBTCUSD"
    assert build_candles_key("tBTCUSD", "1m") == "trade:1m:tBTCUSD"
    assert build_candles_key("BTCUSD", "1d") == "trade:1D:tBTCUSD"


def test_parse_ws_candle() -> None:
    ts_ms = 1700000000000
    raw = [ts_ms, 100.0, 101.0, 102.0, 99.5, 123.456]

    candle = parse_ws_candle(raw, "tBTCUSD", "1h")

    assert candle.exchange == "bitfinex"
    assert candle.symbol == "BTCUSD"
    assert candle.timeframe == "1h"
    assert candle.open_time == datetime.fromtimestamp(ts_ms / 1000, tz=UTC)
    assert candle.close_time == candle.open_time + timedelta(hours=1)
    assert candle.open == Decimal("100.0")
    assert candle.close == Decimal("101.0")
    assert candle.high == Decimal("102.0")
    assert candle.low == Decimal("99.5")
    assert candle.volume == Decimal("123.456")
