from fastapi import APIRouter, Query, HTTPException
from typing import List
from ..services.sentiment import fetch_news_for_asset, analyze_sentiment

router = APIRouter()


@router.get("")
def get_news(symbol: str = Query(..., min_length=1), limit: int = Query(10)) -> List[dict]:
    """Return latest headlines for a symbol with sentiment labels.

    Uses NewsAPI via `services.sentiment` which includes caching to respect
    free-tier limits.
    """
    articles = fetch_news_for_asset(symbol, limit=limit)
    if not articles:
        # Return empty list instead of 404 — frontend can show fallback UI
        return []

    analyzed = analyze_sentiment(articles)
    return analyzed
