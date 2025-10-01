"""Rate limiter helpers.

This module provides a simple in-memory token-bucket (for dev/single-process)
and an optional Redis-backed implementation (recommended for production or
when running multiple uvicorn workers). If the environment variable
REDIS_URL is set and aioredis is importable, the RedisTokenBucket will be
used for async flows. Existing sync callers in the codebase can continue to
use the `allow_alpha_call()` and `allow_news_call()` helpers which will
dispatch to the appropriate implementation.
"""
import os
import time
from threading import Lock
from typing import Optional


class TokenBucket:
    """Simple in-memory token bucket suitable for single-process usage."""
    def __init__(self, rate: float, capacity: int):
        # rate = tokens per second, capacity = max tokens
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last = time.time()
        self._lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self._lock:
            now = time.time()
            elapsed = now - self._last
            self._last = now
            # refill
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False


# Default in-memory buckets (AlphaVantage 5/min, NewsAPI 100/day)
ALPHA_BUCKET = TokenBucket(rate=(5.0 / 60.0), capacity=5)
NEWS_BUCKET = TokenBucket(rate=(100.0 / 86400.0), capacity=100)


# Redis-backed token bucket (async). Falls back to in-memory when Redis is not
# available or not configured.
RedisAvailable = False
RedisClient = None
try:
    import redis.asyncio as redis_async

    RedisAvailable = True
except Exception:
    RedisAvailable = False


class RedisTokenBucket:
    """An async token-bucket implemented in Redis using INCR and EXPIRE.

    Note: This is a best-effort lightweight implementation. It uses a simple
    refill strategy based on a last-update timestamp and may not be perfectly
    accurate under very high contention. For production-grade rate limiting,
    consider Lua scripts or a dedicated rate-limiter service.
    """

    def __init__(self, redis_url: str, key_prefix: str, rate: float, capacity: int):
        if not RedisAvailable:
            raise RuntimeError("redis.asyncio not available; cannot use RedisTokenBucket")
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.rate = rate
        self.capacity = capacity
        self._pool: Optional[redis_async.Redis] = None

    async def _get_redis(self):
        if self._pool is None:
            self._pool = redis_async.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        return self._pool

    async def consume(self, tokens: int = 1) -> bool:
        redis = await self._get_redis()
        ts_key = f"{self.key_prefix}:ts"
        tokens_key = f"{self.key_prefix}:tokens"

        async with redis.client() as conn:
            # Fetch token count and last timestamp
            vals = await conn.mget(tokens_key, ts_key)
            tok_val, ts_val = vals
            now = time.time()
            if tok_val is None or ts_val is None:
                # Initialize
                await conn.set(tokens_key, self.capacity - tokens)
                await conn.set(ts_key, now)
                await conn.expire(tokens_key, 3600)
                await conn.expire(ts_key, 3600)
                return True
            try:
                current_tokens = float(tok_val)
                last_ts = float(ts_val)
            except Exception:
                # Corrupted values — reset
                await conn.set(tokens_key, self.capacity - tokens)
                await conn.set(ts_key, now)
                return True

            elapsed = now - last_ts
            refill = elapsed * self.rate
            new_tokens = min(self.capacity, current_tokens + refill)
            if new_tokens >= tokens:
                # consume and update
                await conn.set(tokens_key, new_tokens - tokens)
                await conn.set(ts_key, now)
                return True
            else:
                # update timestamp to now
                await conn.set(ts_key, now)
                return False


# Factory to provide a RedisTokenBucket when REDIS_URL is configured
_redis_url = os.getenv("REDIS_URL")
_redis_alpha: Optional[RedisTokenBucket] = None
_redis_news: Optional[RedisTokenBucket] = None
if _redis_url and RedisAvailable:
    try:
        _redis_alpha = RedisTokenBucket(redis_url=_redis_url, key_prefix="rate:alpha", rate=(5.0 / 60.0), capacity=5)
        _redis_news = RedisTokenBucket(redis_url=_redis_url, key_prefix="rate:news", rate=(100.0 / 86400.0), capacity=100)
    except Exception:
        _redis_alpha = None
        _redis_news = None


def allow_alpha_call() -> bool:
    """Sync-friendly helper used by existing code.

    If REDIS_URL is configured and aioredis is available, the async Redis
    bucket should be used by async code paths. For simplicity we allow the
    sync callers to use the in-memory bucket.
    """
    return ALPHA_BUCKET.consume(1)


def allow_news_call() -> bool:
    return NEWS_BUCKET.consume(1)


async def allow_alpha_call_async() -> bool:
    """Async-aware helper that prefers Redis when available, else falls back.

    Use this from async code paths that may run in multiple workers.
    """
    if _redis_alpha is not None:
        try:
            return await _redis_alpha.consume(1)
        except Exception:
            # Fall back to in-memory
            return ALPHA_BUCKET.consume(1)
    return ALPHA_BUCKET.consume(1)


async def allow_news_call_async() -> bool:
    if _redis_news is not None:
        try:
            return await _redis_news.consume(1)
        except Exception:
            return NEWS_BUCKET.consume(1)
    return NEWS_BUCKET.consume(1)
