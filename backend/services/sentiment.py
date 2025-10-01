"""News fetching and FinBERT sentiment skeleton with simple in-memory cache.

This module provides:
- fetch_news_for_asset(symbol, limit): returns list of headlines (uses NewsAPI)
- analyze_sentiment(headlines): placeholder that returns polarity per headline

Caching: results cached for NEWS_CACHE_TTL seconds (default 15 minutes) to
avoid exhausting the free NewsAPI quota.
"""
import os
import time
import requests
from typing import List, Dict

# Cache structure: {symbol: (timestamp, data)}
_NEWS_CACHE: Dict[str, tuple] = {}
NEWS_CACHE_TTL = int(os.getenv('NEWS_CACHE_TTL', 900))  # 15 minutes default


def fetch_news_for_asset(symbol: str, limit: int = 20) -> List[Dict]:
    """Fetch latest news for symbol using NewsAPI with caching.

    Returns a list of dict {headline, source, url, publishedAt}
    """
    now = time.time()
    key = symbol.upper()
    cached = _NEWS_CACHE.get(key)
    if cached:
        ts, data = cached
        if now - ts < NEWS_CACHE_TTL:
            return data

    api_key = os.getenv('NEWSAPI_KEY') or os.getenv('NEWS_API_KEY')
    if not api_key:
        # No key present — return empty list as safe fallback
        _NEWS_CACHE[key] = (now, [])
        return []

    # Respect a global news rate-limiter if present
    # Prefer async Redis-backed limiter if available to coordinate across
    # workers. We call the async helper in a short-lived event loop; this is
    # acceptable for occasional news fetches. Fall back to the in-memory
    # sync limiter when Redis/aioredis is not available.
    try:
        from .rate_limiter import allow_news_call_async, allow_news_call
        import asyncio

        # We are in a synchronous function. If there is an active event loop
        # (meaning this code is being executed from async context), fall back
        # to the sync helper to avoid awaiting inside a sync function. If no
        # loop is running, run the async helper via asyncio.run.
        allowed = False
        try:
            loop = asyncio.get_running_loop()
            # If here, an event loop is running — use sync helper to avoid
            # blocking or complicated bridging.
            allowed = allow_news_call()
        except RuntimeError:
            # No running loop in this thread; safe to run the async helper
            try:
                allowed = asyncio.run(allow_news_call_async())
            except Exception:
                allowed = allow_news_call()
        except Exception:
            try:
                allowed = allow_news_call()
            except Exception:
                allowed = False

        if not allowed:
            _NEWS_CACHE[key] = (now, [])
            return []
    except Exception:
        # If limiter import fails, continue (safe default)
        pass

    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': symbol,
        'sortBy': 'publishedAt',
        'language': 'en',
        'pageSize': min(limit, 100),
        'apiKey': api_key,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        payload = r.json()
        articles = payload.get('articles', [])
        out = []
        for a in articles:
            out.append({
                'headline': a.get('title'),
                'source': a.get('source', {}).get('name'),
                'url': a.get('url'),
                'publishedAt': a.get('publishedAt'),
            })

        _NEWS_CACHE[key] = (now, out)
        return out
    except Exception:
        # On any failure, cache empty result briefly to avoid tight retries
        _NEWS_CACHE[key] = (now, [])
        return []


def analyze_sentiment(headlines: List[Dict]) -> List[Dict]:
    """Placeholder sentiment analyzer.

    Returns list of {headline, sentiment: 'positive'|'neutral'|'negative'}.
    Replace with FinBERT pipeline in model_finbert.py when ready.
    """
    # If FINBERT_MODEL is set, try to use FinBERT pipeline for higher accuracy.
    model_name = os.getenv('FINBERT_MODEL') or os.getenv('FINBERT_PATH')
    if model_name:
        try:
            from .finbert import analyze_with_finbert

            return analyze_with_finbert(headlines, model_name)
        except Exception:
            # Fall back to heuristic if transformers or model not available
            pass

    out = []
    for h in headlines:
        text = (h.get('headline') or '').lower()
        if any(w in text for w in ['gain', 'beat', 'rise', 'surge', 'bull']):
            sentiment = 'positive'
        elif any(w in text for w in ['drop', 'miss', 'fall', 'bear', 'decline']):
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        out.append({**h, 'sentiment': sentiment})
    return out
