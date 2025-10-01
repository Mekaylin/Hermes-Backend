import pytest
import sys, os, types
from fastapi.testclient import TestClient

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
backend_pkg = types.ModuleType('backend')
backend_pkg.__path__ = [os.path.join(repo_root, 'backend')]
sys.modules['backend'] = backend_pkg
import backend.app as _appmod
app = _appmod.app


def fake_fetch_news_for_asset(symbol, limit=10):
    return [
        {'headline': 'Company posts strong earnings', 'source': 'Demo', 'url': 'http://example.com', 'publishedAt': '2021-01-01T00:00:00Z'},
        {'headline': 'Market sees minor dip', 'source': 'News', 'url': 'http://example.com/2', 'publishedAt': '2021-01-02T00:00:00Z'},
    ]


def fake_analyze_sentiment(headlines):
    return [
        {**headlines[0], 'sentiment': 'positive'},
        {**headlines[1], 'sentiment': 'neutral'},
    ]


def test_news(monkeypatch):
    import importlib
    news_router = importlib.import_module('backend.routers.news')
    monkeypatch.setattr(news_router, 'fetch_news_for_asset', fake_fetch_news_for_asset)
    monkeypatch.setattr(news_router, 'analyze_sentiment', fake_analyze_sentiment)

    client = TestClient(app)
    resp = client.get('/news', params={'symbol': 'AAPL', 'limit': 2})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]['sentiment'] == 'positive'
