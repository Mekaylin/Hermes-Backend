import os
import requests
import asyncio
from config import ALPHA_VANTAGE_API_KEY, BINANCE_API_KEY
try:
	# prefer async helper when available
	from .services.rate_limiter import allow_alpha_call_async as _allow_alpha_async, allow_alpha_call as _allow_alpha_sync
except Exception:
	_allow_alpha_async = None
	from .services.rate_limiter import allow_alpha_call as _allow_alpha_sync

try:
	from .services.binance_ws import get_latest_candle, start_stream
except Exception:
	get_latest_candle = None
	start_stream = None

def fetch_alpha_vantage_ohlcv(symbol="BTCUSD", interval="1min"):
	url = f"https://www.alphavantage.co/query"
	params = {
		"function": "TIME_SERIES_INTRADAY",
		"symbol": symbol,
		"interval": interval,
		"apikey": ALPHA_VANTAGE_API_KEY
	}
	r = requests.get(url, params=params)
	return r.json()

def fetch_binance_ohlcv(symbol="BTCUSDT", interval="1m"):
	url = f"https://api.binance.com/api/v3/klines"
	params = {
		"symbol": symbol,
		"interval": interval,
		"limit": 100
	}
	r = requests.get(url, params=params)
	return r.json()


def fetch_news(symbol="BTC"):
	# Example using NewsAPI (replace with your API key)
	NEWS_API_KEY = os.getenv("NEWS_API_KEY")
	url = f"https://newsapi.org/v2/everything"
	params = {
		"q": symbol,
		"sortBy": "publishedAt",
		"apiKey": NEWS_API_KEY,
		"language": "en"
	}
	r = requests.get(url, params=params)
	return r.json()

# Technical indicators
import pandas as pd

def calculate_ema(df, period=14, column='close'):
	return df[column].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14, column='close'):
	delta = df[column].diff()
	gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
	loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
	rs = gain / loss
	rsi = 100 - (100 / (1 + rs))
	import os
	import time
	import requests
	from config import ALPHA_VANTAGE_API_KEY, BINANCE_API_KEY
	from typing import Optional, Dict, Any

	# Simple in-memory rate limiting trackers
	# For Alpha Vantage: allow up to ALPHA_MAX_PER_MIN calls per minute
	ALPHA_MAX_PER_MIN = int(os.getenv('ALPHAVANTAGE_RPM', 5))
	_alpha_timestamps = []  # list of epoch seconds of recent calls

	# For Binance: per-symbol cooldown in seconds (1s per symbol typical free limit)
	BINANCE_COOLDOWN = float(os.getenv('BINANCE_COOLDOWN_S', 1.0))
	_binance_last_call: Dict[str, float] = {}


	def _throttle_alpha():
		now = time.time()
		# drop timestamps older than 60 seconds
		window = 60
		while _alpha_timestamps and now - _alpha_timestamps[0] > window:
			_alpha_timestamps.pop(0)

		if len(_alpha_timestamps) >= ALPHA_MAX_PER_MIN:
			# Sleep until the oldest timestamp exits the window
			wait = window - (now - _alpha_timestamps[0]) + 0.1
			time.sleep(max(0.1, wait))

		_alpha_timestamps.append(time.time())


	def _throttle_binance(symbol: str):
		now = time.time()
		last = _binance_last_call.get(symbol)
		if last:
			elapsed = now - last
			if elapsed < BINANCE_COOLDOWN:
				time.sleep(BINANCE_COOLDOWN - elapsed)
		_binance_last_call[symbol] = time.time()


	def fetch_alpha_vantage_ohlcv(symbol: str = "BTCUSD", interval: str = "1min") -> Dict[str, Any]:
		"""Fetch intraday OHLCV from Alpha Vantage with simple throttling.

		NOTE: This is synchronous and will block; in production use an async queue
		or a centralized rate-limiter for better concurrency.
		"""
		if not ALPHA_VANTAGE_API_KEY:
			return {}

		# Respect token-bucket allowance; prefer async-aware helper when available
		try:
			if _allow_alpha_async is not None:
				# run the async helper in the current thread loop if needed
				loop = asyncio.get_event_loop()
				allowed = loop.run_until_complete(_allow_alpha_async()) if loop and loop.is_running() is False else asyncio.run(_allow_alpha_async())
			else:
				allowed = _allow_alpha_sync()
		except Exception:
			# on any error, conservatively deny
			allowed = False

		if not allowed:
			return {}

		_throttle_alpha()
		url = "https://www.alphavantage.co/query"
		params = {
			"function": "TIME_SERIES_INTRADAY",
			"symbol": symbol,
			"interval": interval,
			"apikey": ALPHA_VANTAGE_API_KEY
		}
		r = requests.get(url, params=params, timeout=10)
		r.raise_for_status()
		return r.json()


	def fetch_binance_ohlcv(symbol: str = "BTCUSDT", interval: str = "1m") -> Any:
		"""Fetch kline data from Binance with minimal per-symbol cooldown.

		This function does not attempt to authenticate; for private endpoints
		you would include API keys and signatures. For public kline data, it's
		sufficient to call the REST endpoint.
		"""
		_throttle_binance(symbol)

		url = "https://api.binance.com/api/v3/klines"
		params = {"symbol": symbol, "interval": interval, "limit": 500}
		r = requests.get(url, params=params, timeout=10)
		r.raise_for_status()
		return r.json()


	def fetch_market(symbol: str, interval: str = "1m") -> Any:
		"""Synchronous wrapper kept for compatibility: prefer REST providers.

		Use `fetch_market_async` from async code to prefer websocket streaming.
		"""
		s = symbol.upper()
		try:
			if s.endswith('USDT') or 'BTC' in s or 'ETH' in s:
				return fetch_binance_ohlcv(symbol=s, interval=interval)
			else:
				# For stocks/forex, prefer Alpha Vantage if key present
				if ALPHA_VANTAGE_API_KEY:
					return fetch_alpha_vantage_ohlcv(symbol=s, interval=interval)
				return {}
		except Exception:
			return {}


	async def fetch_market_async(symbol: str, interval: str = "1m") -> Any:
		"""Async wrapper: prefer websocket latest candle for crypto symbols,
		fallback to REST if streaming not available or no data.
		"""
		s = symbol.upper()
		try:
			if s.endswith('USDT') or 'BTC' in s or 'ETH' in s:
				if start_stream is not None:
					# ensure a background stream is started; start_stream is a no-op
					# if websockets isn't installed or streaming is unavailable.
					try:
						await start_stream(s, interval)
					except Exception:
						pass
				if get_latest_candle is not None:
					latest = await get_latest_candle(s)
					if latest:
						return {'candles': [latest]}
				# fallback to REST
				loop = asyncio.get_running_loop()
				return await loop.run_in_executor(None, fetch_binance_ohlcv, s, interval)
			else:
				if ALPHA_VANTAGE_API_KEY:
					loop = asyncio.get_running_loop()
					return await loop.run_in_executor(None, fetch_alpha_vantage_ohlcv, s, interval)
				return {}
		except Exception:
			return {}
