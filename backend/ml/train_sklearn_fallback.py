"""Train a tiny sklearn model and save to the LightGBM artifact path.

This allows the backend to load a model via joblib without requiring the
LightGBM native library during local development.
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib


def make_synthetic_data(n=500):
    rng = np.random.RandomState(1)
    df = pd.DataFrame({
        'close': rng.normal(100, 5, size=n),
        'ema_12': rng.normal(100, 5, size=n),
        'ema_26': rng.normal(100, 5, size=n),
        'rsi_14': rng.uniform(20, 80, size=n),
        'macd': rng.normal(0, 1, size=n),
    })
    df['target'] = (rng.normal(0, 0.02, size=n) > 0).astype(int)
    return df


def train_and_save(out_path='backend/ml/artifacts/lightgbm_model.pkl'):
    df = make_synthetic_data()
    X = df[['close', 'ema_12', 'ema_26', 'rsi_14', 'macd']]
    y = df['target']

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X_train, y_train)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(clf, out_path)
    print('Saved sklearn fallback model to', out_path)


if __name__ == '__main__':
    train_and_save()
