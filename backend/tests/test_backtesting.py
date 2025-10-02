import os
import sys
import sqlite3
from datetime import datetime, timedelta
from types import SimpleNamespace, ModuleType

import pytest


def test_run_backtest_structure(monkeypatch, tmp_path):
    # Inject a lightweight fake backend.agent module to avoid heavy AI deps (transformers)
    fake_agent_mod = ModuleType('backend.agent')

    class Signal:
        BUY = 'BUY'
        SELL = 'SELL'
        HOLD = 'HOLD'

    async def fake_analyze_asset(self, symbol, timeframe='1d'):
        return SimpleNamespace(
            symbol=symbol,
            signal=Signal.HOLD,
            confidence=50.0,
            reasoning=['synthetic test prediction'],
            entry_price=None,
            stop_loss=None,
            target_price=None,
            timestamp=datetime.utcnow(),
            timeframe=timeframe,
            risk_level='LOW'
        )

    class TradingAgent:
        def __init__(self, *args, **kwargs):
            pass

        analyze_asset = fake_analyze_asset

    fake_agent_mod.TradingAgent = TradingAgent  # type: ignore[attr-defined]
    fake_agent_mod.Signal = Signal  # type: ignore[attr-defined]
    # Minimal TradingPrediction placeholder (engine only imports type)
    class TradingPrediction:
        pass
    fake_agent_mod.TradingPrediction = TradingPrediction  # type: ignore[attr-defined]

    sys.modules['backend.agent'] = fake_agent_mod

    # Now import engine (it will import our fake backend.agent)
    from backend.backtesting.engine import run_backtest, DB_PATH

    # Use a short, recent range
    end = datetime.utcnow().date()
    start = end - timedelta(days=30)

    result = run_backtest('SPY', start.isoformat(), end.isoformat())

    assert 'backtest_id' in result
    assert 'metrics' in result
    assert 'equity_curve' in result
    assert isinstance(result['equity_curve'], list)

    # Check DB contains the backtest row
    assert os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, symbol FROM backtests WHERE id = ?', (result['backtest_id'],))
    row = cur.fetchone()
    conn.close()
    assert row is not None
    assert row[1] == 'SPY'
