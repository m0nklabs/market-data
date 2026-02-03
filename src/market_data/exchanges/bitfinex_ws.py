"""Bitfinex public WebSocket client for realtime candle ingestion."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import websockets

from market_data.exchanges.bitfinex import TIMEFRAMES
from market_data.types import Candle

logger = logging.getLogger(__name__)

WS_URL = "wss://api-pub.bitfinex.com/ws/2"


def _api_symbol(symbol: str) -> str:
    return symbol if symbol.startswith("t") else f"t{symbol}"


def _api_timeframe(timeframe: str) -> str:
    return TIMEFRAMES.get(timeframe, (timeframe, timedelta(hours=1)))[0]


def _timeframe_delta(timeframe: str) -> timedelta:
    return TIMEFRAMES.get(timeframe, ("1h", timedelta(hours=1)))[1]


def build_candles_key(symbol: str, timeframe: str) -> str:
    """Build Bitfinex WS candles key, e.g. trade:1m:tBTCUSD."""
    return f"trade:{_api_timeframe(timeframe)}:{_api_symbol(symbol)}"


def parse_ws_candle(raw: list[Any], symbol: str, timeframe: str) -> Candle:
    """Parse a WS candle payload into a Candle.

    Payload format: [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
    """
    ts_ms, open_, close_, high_, low_, volume = raw

    open_time = datetime.fromtimestamp(ts_ms / 1000, tz=UTC)
    close_time = open_time + _timeframe_delta(timeframe)

    return Candle(
        exchange="bitfinex",
        symbol=symbol.lstrip("t"),
        timeframe=timeframe,
        open_time=open_time,
        close_time=close_time,
        open=Decimal(str(open_)),
        high=Decimal(str(high_)),
        low=Decimal(str(low_)),
        close=Decimal(str(close_)),
        volume=Decimal(str(abs(volume))),
    )


@dataclass(frozen=True)
class CandleSubscription:
    symbol: str
    timeframe: str

    @property
    def key(self) -> str:
        return build_candles_key(self.symbol, self.timeframe)


class BitfinexCandleWSClient:
    """Reconnect-capable Bitfinex WS client that emits candles via callback."""

    def __init__(
        self,
        subscriptions: list[CandleSubscription],
        on_candles: Callable[[list[Candle]], Awaitable[None]] | Callable[[list[Candle]], None],
        reconnect_initial_backoff: float = 1.0,
        reconnect_max_backoff: float = 60.0,
    ):
        self._subscriptions = subscriptions
        self._on_candles = on_candles
        self._reconnect_initial_backoff = reconnect_initial_backoff
        self._reconnect_max_backoff = reconnect_max_backoff

        self._stop_event = asyncio.Event()

    def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        backoff = self._reconnect_initial_backoff

        while not self._stop_event.is_set():
            try:
                await self._connect_and_stream()
                backoff = self._reconnect_initial_backoff
            except asyncio.CancelledError:
                raise
            except Exception as e:
                if self._stop_event.is_set():
                    break
                logger.warning(f"WS error: {e}. Reconnecting in {backoff:.1f}s")
                await asyncio.sleep(backoff)
                backoff = min(self._reconnect_max_backoff, max(backoff * 2, self._reconnect_initial_backoff))

    async def _connect_and_stream(self) -> None:
        chan_id_to_sub: dict[int, CandleSubscription] = {}
        pending_key_to_sub = {sub.key: sub for sub in self._subscriptions}

        logger.info(f"Connecting Bitfinex WS ({len(self._subscriptions)} candle subscriptions)")

        async with websockets.connect(
            WS_URL,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=10,
            max_size=2**20,
        ) as ws:
            # Subscribe to all candle channels.
            for sub in self._subscriptions:
                msg = {"event": "subscribe", "channel": "candles", "key": sub.key}
                await ws.send(json.dumps(msg))

            while not self._stop_event.is_set():
                raw = await ws.recv()
                message = json.loads(raw)

                # Event messages
                if isinstance(message, dict):
                    event = message.get("event")
                    if event == "subscribed" and message.get("channel") == "candles":
                        chan_id = int(message["chanId"])
                        key = message.get("key")
                        if not isinstance(key, str):
                            continue

                        sub = pending_key_to_sub.get(key)
                        if sub:
                            chan_id_to_sub[chan_id] = sub
                            logger.info(f"WS subscribed: {sub.symbol}/{sub.timeframe} (chanId={chan_id})")
                        continue

                    if event == "error":
                        code = message.get("code")
                        msg = message.get("msg")
                        raise RuntimeError(f"Bitfinex WS error {code}: {msg}")

                    # ignore info/other
                    continue

                # Data messages
                if not isinstance(message, list) or len(message) < 2:
                    continue

                chan_id = message[0]
                payload = message[1]

                if payload == "hb":
                    continue

                sub = chan_id_to_sub.get(int(chan_id))
                if not sub:
                    continue

                # Snapshot: [chanId, [ [..], [..] ]]
                if isinstance(payload, list) and payload and isinstance(payload[0], list):
                    latest_item = max(payload, key=lambda item: item[0])
                    candle = parse_ws_candle(latest_item, sub.symbol, sub.timeframe)
                    await self._emit([candle])
                    continue

                # Update: [chanId, [..]]
                if isinstance(payload, list) and len(payload) == 6:
                    candle = parse_ws_candle(payload, sub.symbol, sub.timeframe)
                    await self._emit([candle])

    async def _emit(self, candles: list[Candle]) -> None:
        if not candles:
            return

        result = self._on_candles(candles)
        if asyncio.iscoroutine(result):
            await result
