"""Train a model from historical OHLCV using yfinance.

This script is conservative: it will use LightGBM if importable and lib deps
are satisfied; otherwise it falls back to a sklearn RandomForest. It writes
the trained artifact to `backend/ml/artifacts/lightgbm_model.pkl` to match
the MLModel loader.
"""
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / roll_down.replace(0, np.nan)
    df['rsi_14'] = 100 - (100 / (1 + rs)).fillna(50)
    df['macd'] = df['ema_12'] - df['ema_26']
    df = df.dropna()
    return df


def train(symbol='BTC-USD', period='180d', interval='1h', out_path='backend/ml/artifacts/lightgbm_model.pkl'):
    try:
        import yfinance as yf
    except Exception as e:
        raise RuntimeError('yfinance is required for historical training') from e

    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval)
    if hist.empty:
        raise RuntimeError('no historical data fetched')

    df = compute_indicators(hist)
    X = df[['Close', 'ema_12', 'ema_26', 'rsi_14', 'macd']]
    # target: next period return > 0
    y = (df['Close'].shift(-1) - df['Close']) / df['Close']
    y = (y > 0).astype(int)[:-1]
    X = X[:-1]

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Try LightGBM first
    try:
        import lightgbm as lgb
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val)
        params = {'objective': 'binary', 'metric': 'binary_logloss', 'verbosity': -1, 'seed': 42}
        model = lgb.train(params, train_data, num_boost_round=100, valid_sets=[val_data], early_stopping_rounds=10)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        joblib.dump(model, out_path)
        print('Saved LightGBM model to', out_path)
        return out_path
    except Exception:
        # fallback to sklearn
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        joblib.dump(clf, out_path)
        print('Saved sklearn fallback model to', out_path)
        return out_path


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--symbol', default='BTC-USD')
    p.add_argument('--period', default='180d')
    p.add_argument('--interval', default='1h')
    p.add_argument('--out', default='backend/ml/artifacts/lightgbm_model.pkl')
    args = p.parse_args()
    train(symbol=args.symbol, period=args.period, interval=args.interval, out_path=args.out)
