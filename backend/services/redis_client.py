"""Redis client helper with optional async client and health-check.

This module attempts to import `redis.asyncio` (redis-py v4+). If not
available it gracefully falls back to a no-op client and reports status.
"""
from typing import Optional, Any
import os
import asyncio

RedisAvailable = False
_redis = None

try:
    import redis.asyncio as redis_async

    RedisAvailable = True
    _redis = None
except Exception:
    # redis.asyncio not available
    RedisAvailable = False
    _redis = None


async def get_redis_client() -> Optional[Any]:
    """Return a connected redis.asyncio client or None.

    The client is created on first call and re-used. If REDIS_URL is not set
    or redis is unavailable, returns None.
    """
    global _redis
    if not RedisAvailable:
        return None

    if _redis is None:
        url = os.getenv('REDIS_URL')
        if not url:
            return None
        try:
            _redis = redis_async.from_url(url, decode_responses=True)
            # test connection
            await _redis.ping()
        except Exception:
            _redis = None
    return _redis


async def get_redis_status() -> dict:
    """Return a small dict with redis connection status for /health."""
    client = await get_redis_client()
    if client is None:
        return {'available': False}
    try:
        pong = await client.ping()
        return {'available': bool(pong)}
    except Exception:
        return {'available': False}
