from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..services.ml_model import MLModel
from ..services.market_client import fetch_candles
from ..services.indicators import compute_indicators
from .. import db as _db
from ..models import Asset, Prediction
from datetime import datetime

router = APIRouter()

ml_model = MLModel()


@router.get("")
async def predict(symbol: str = Query(...), tf: str = Query("1h")):
    """Return AI trading signal for a symbol.

    Output format: {"signal":"BUY","confidence":0.85,"predicted_change":0.03}
    """
    df = await fetch_candles(symbol, tf)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Market data not found for symbol")

    indicators = compute_indicators(df)
    result = ml_model.predict(df, indicators, symbol, tf)

    # Normalize response to required shape
    signal = result.get('signal', 'HOLD')
    confidence = float(result.get('confidence', 0.0))
    predicted_change = float(result.get('predicted_change', result.get('predicted_pct_change', 0.0)))

    # Try to persist prediction if DB available (safe no-op on failure)
    try:
        if getattr(_db, 'SessionLocal', None):
            db = _db.SessionLocal()
            asset = db.query(Asset).filter(Asset.symbol == symbol).first()
            if not asset:
                # Create a minimal asset record if missing (category unknown)
                try:
                    from ..models import AssetCategory
                    category = AssetCategory.stocks
                except Exception:
                    category = 'stocks'
                asset = Asset(symbol=symbol, name=symbol, category=category)
                db.add(asset)
                db.commit()
                db.refresh(asset)

            pred = Prediction(
                asset_id=asset.id,
                timestamp=datetime.utcnow(),
                signal=signal,
                confidence=confidence,
                entry=float(result.get('entry', 0.0)),
                target=float(result.get('target', 0.0)),
                stop=float(result.get('stop', 0.0)),
                rationale=str(result.get('rationale', '')),
            )
            db.add(pred)
            db.commit()
    except Exception:
        # DB not available or other error; don't block response
        pass

    return {"signal": signal, "confidence": confidence, "predicted_change": predicted_change}
