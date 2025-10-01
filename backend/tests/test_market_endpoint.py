import pandas as pd
import pytest
import sys, os, types, importlib
from fastapi.testclient import TestClient

# Ensure a proper `backend` package exists so relative imports inside
# backend/app.py work when pytest's working directory is the backend/ folder.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
backend_pkg = types.ModuleType('backend')
backend_pkg.__path__ = [os.path.join(repo_root, 'backend')]
sys.modules['backend'] = backend_pkg
import backend.app as _appmod
app = _appmod.app


def make_df():
    return pd.DataFrame([
        {
            'timestamp': pd.Timestamp('2021-01-01T00:00:00Z'),
            'open': 100.0,
            'high': 110.0,
            'low': 95.0,
            'close': 105.0,
            'volume': 1000,
        }
    ])


def test_market_symbol(monkeypatch):
    # Ensure service modules are importable and present on the backend package
    import importlib
    # Patch the router-level references that were bound at import time
    market_router = importlib.import_module('backend.routers.market')
    ind = importlib.import_module('backend.services.indicators')

    # patch async fetch_candles to return a small DataFrame
    async def fake_fetch_candles(symbol, tf='1m'):
        return make_df()

    def fake_compute_indicators(df):
        # return a small DataFrame with indicator columns used by router
        return pd.DataFrame([{
            'ema_12': 102.0,
            'rsi_14': 55.0,
            'macd': 0.5,
            'bb_upper': 110.0,
            'bb_lower': 90.0,
        }])

    monkeypatch.setattr(market_router, 'fetch_candles', fake_fetch_candles)
    monkeypatch.setattr(market_router, 'compute_indicators', fake_compute_indicators)

    client = TestClient(app)
    resp = client.get('/market', params={'symbol': 'BTCUSDT', 'tf': '1h'})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('symbol') == 'BTCUSDT'
    assert isinstance(data.get('ohlcv'), list)
    assert 'indicators' in data
