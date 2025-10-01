"""Lightweight Binance websocket candle streamer.

This module provides a simple async helper to subscribe to kline updates for
public symbols via Binance's websocket stream. It is intentionally minimal and
keeps an in-memory latest-candle cache per symbol for consumers to read.

Usage (simple):
    await start_stream('btcusdt', '1m')
    latest = await get_latest_candle('BTCUSDT')

The streamer uses websockets and asyncio; if websockets isn't available the
module will remain a no-op and callers should fall back to REST polling.
"""
import asyncio
import json
import logging
from typing import Dict, Optional

log = logging.getLogger(__name__)

_latest: Dict[str, Dict] = {}
_tasks: Dict[str, asyncio.Task] = {}

try:
    import websockets
except Exception:
    websockets = None


async def _stream_symbol(symbol: str, interval: str = '1m'):
    s = symbol.lower()
    stream = f"wss://stream.binance.com:9443/ws/{s}@kline_{interval}"
    if not websockets:
        log.warning('websockets not available; cannot stream %s', symbol)
        return

    while True:
        try:
            async with websockets.connect(stream) as ws:
                async for msg in ws:
                    payload = json.loads(msg)
                    k = payload.get('k') or {}
                    # k contains open time, close time, open, high, low, close, etc.
                    candle = {
                        'open_time': k.get('t'),
                        'open': float(k.get('o', 0)),
                        'high': float(k.get('h', 0)),
                        'low': float(k.get('l', 0)),
                        'close': float(k.get('c', 0)),
                        'volume': float(k.get('v', 0)),
                        'is_closed': bool(k.get('x', False)),
                        'close_time': k.get('T'),
                    }
                    _latest[s.upper()] = candle
        except Exception as e:
            log.exception('Binance websocket error for %s: %s', symbol, e)
            await asyncio.sleep(2)


async def start_stream(symbol: str, interval: str = '1m') -> None:
    s = symbol.upper()
    if s in _tasks:
        return
    if not websockets:
        log.debug('websockets not installed; skipping stream for %s', s)
        return
    loop = asyncio.get_running_loop()
    task = loop.create_task(_stream_symbol(s, interval))
    _tasks[s] = task


async def stop_stream(symbol: str) -> None:
    s = symbol.upper()
    t = _tasks.get(s)
    if t:
        t.cancel()
        _tasks.pop(s, None)


async def get_latest_candle(symbol: str) -> Optional[Dict]:
    return _latest.get(symbol.upper())
