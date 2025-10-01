import pandas as pd
import pytest
import sys, os, types
from fastapi.testclient import TestClient

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
backend_pkg = types.ModuleType('backend')
backend_pkg.__path__ = [os.path.join(repo_root, 'backend')]
sys.modules['backend'] = backend_pkg
import backend.app as _appmod
app = _appmod.app


class DummyModel:
    def predict(self, df, indicators, symbol, tf):
        return {'signal': 'BUY', 'confidence': 0.85, 'predicted_change': 0.03}


async def fake_fetch_candles(symbol, tf='1h'):
    import pandas as pd
    return pd.DataFrame([
        {'timestamp': pd.Timestamp('2021-01-01T00:00:00Z'), 'open': 1, 'high': 2, 'low': 1, 'close': 1.5, 'volume': 10}
    ])


def test_predict(monkeypatch):
    import importlib
    pred_mod = importlib.import_module('backend.routers.predict')
    # Patch the router-level objects used by the predict router
    monkeypatch.setattr(pred_mod, 'ml_model', DummyModel())
    monkeypatch.setattr(pred_mod, 'fetch_candles', fake_fetch_candles)

    client = TestClient(app)
    resp = client.get('/predict', params={'symbol': 'BTCUSDT', 'tf': '1h'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['signal'] == 'BUY'
    assert data['confidence'] == pytest.approx(0.85)
