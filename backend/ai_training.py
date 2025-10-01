"""
Lightweight training/testing helpers for development.

These are intentionally simple: they simulate a short training run
and write a metrics file. In production you'd replace these with
proper data loaders, model training code, checkpointing, etc.
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
import yfinance as yf

BASE = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)


def train_agent(
    epochs: int = 3,
    symbol: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    csv_path: Optional[str] = None
) -> Dict[str, Any]:
    """Train on historical data supplied by symbol+date-range or CSV file.

    This is still a lightweight simulator for dev use. If csv_path is
    provided, the CSV is loaded. Otherwise, if symbol is provided we
    fetch history via yfinance for the given date range.

    Returns a dict with model_path and training history/metrics.
    """
    # Load data
    df = None
    if csv_path:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")
        df = pd.read_csv(csv_path, parse_dates=True)
    elif symbol and start_date and end_date:
        # Use yfinance to download OHLCV
        df = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if df is None or df.empty:
            raise ValueError(f"No market data for {symbol} between {start_date} and {end_date}")
    else:
        # No data provided — run a tiny dry training using synthetic data
        df = pd.DataFrame({'close': [1.0, 1.01, 1.02, 0.99, 1.03]})

    # Simulate training loop using the provided data's size to influence epochs
    data_len = len(df)
    history = []
    effective_epochs = max(1, min(epochs, 10))
    for epoch in range(1, effective_epochs + 1):
        # Simulate work proportional to data size but keep short for dev
        time.sleep(0.2)
        loss = max(0.01, 1.0 / (epoch + (data_len / 1000.0) + 1))
        acc = min(0.99, 0.5 + epoch * 0.05 + min(0.4, data_len / 10000.0))
        history.append({'epoch': epoch, 'loss': loss, 'accuracy': acc, 'timestamp': datetime.utcnow().isoformat()})

    model_path = os.path.join(MODEL_DIR, f'model_{int(time.time())}.json')
    with open(model_path, 'w') as f:
        json.dump({'trained_at': datetime.utcnow().isoformat(), 'history': history, 'data_rows': data_len}, f)

    # Return summary
    metrics = {
        'model_path': model_path,
        'history': history,
        'data_rows': data_len,
        'trained_at': datetime.utcnow().isoformat()
    }
    return metrics


def test_agent() -> Dict[str, Any]:
    """Run a small synthetic evaluation and return metrics."""
    # Simulate test
    time.sleep(0.2)
    metrics = {'accuracy': 0.78, 'f1': 0.74, 'evaluated_at': datetime.utcnow().isoformat()}
    return metrics
