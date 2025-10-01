from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from .. import db as _db
from ..models import Asset
from ..services.market_client import fetch_candles
from ..services.indicators import compute_indicators
import pandas as pd

router = APIRouter()


@router.get("")
async def get_market(symbol: Optional[str] = Query(None), tf: str = "1m"):
    """Return OHLCV + indicators for a symbol, or list assets if no symbol provided.

    Output matches the required JSON shape with 'ohlcv' and 'indicators'.
    """
    db = None
    if getattr(_db, 'SessionLocal', None):
        db = _db.SessionLocal()
    try:
        if not symbol:
            if db is None:
                return []
            assets = db.query(Asset).limit(50).all()
            return [{"symbol": a.symbol, "name": a.name, "category": (a.category.value if hasattr(a, 'category') else str(a.category))} for a in assets]

        # Fetch candles via adapters (yfinance / binance / alpha fallback)
        df = await fetch_candles(symbol, tf)
        if df is None or df.empty:
            # Fallback: return HTTP 404 to indicate no data
            raise HTTPException(status_code=404, detail="Market data not found for symbol")

        # Ensure timestamp is serializable
        df = df.copy()
        if 'timestamp' in df.columns:
            df['time'] = pd.to_datetime(df['timestamp']).astype(str)
        else:
            df['time'] = df.index.astype(str)

        # Compute indicators
        indicators_df = compute_indicators(df)

        # Prepare OHLCV list
        ohlcv = []
        for _, row in df.iterrows():
            ohlcv.append({
                "time": str(row.get('time')),
                "open": float(row.get('open') or 0),
                "high": float(row.get('high') or 0),
                "low": float(row.get('low') or 0),
                "close": float(row.get('close') or 0),
                "volume": float(row.get('volume') or 0),
            })

        # Top-level indicators (use last row values)
        last = indicators_df.iloc[-1] if not indicators_df.empty else None
        indicators = {
            "ema": float(last.get('ema_12', 0)) if last is not None else 0,
            "rsi": float(last.get('rsi_14', 0)) if last is not None else 0,
            "macd": float(last.get('macd', 0)) if last is not None else 0,
            "bollinger": {
                "upper": float(last.get('bb_upper', 0)) if last is not None else 0,
                "lower": float(last.get('bb_lower', 0)) if last is not None else 0,
            },
        }

        return {"symbol": symbol, "ohlcv": ohlcv, "indicators": indicators}
    finally:
        db.close()
