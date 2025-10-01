"""Tiny LightGBM trainer for local experimentation.

Generates synthetic features and trains a small LightGBM model, saving the
artifact to `backend/ml/artifacts/lightgbm_model.pkl`.
"""
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib
import lightgbm as lgb


def make_synthetic_data(n=2000):
    rng = np.random.RandomState(42)
    df = pd.DataFrame({
        'close': rng.normal(100, 10, size=n),
        'ema_12': rng.normal(100, 10, size=n),
        'ema_26': rng.normal(100, 10, size=n),
        'rsi_14': rng.uniform(20, 80, size=n),
        'macd': rng.normal(0, 1, size=n),
    })
    # target: next-period return
    df['target'] = (rng.normal(0, 0.02, size=n)).astype(float)
    return df


def train_and_save(out_path='backend/ml/artifacts/lightgbm_model.pkl'):
    df = make_synthetic_data()
    X = df[['close', 'ema_12', 'ema_26', 'rsi_14', 'macd']]
    y = (df['target'] > 0).astype(int)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val)

    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'verbosity': -1,
        'seed': 42,
    }

    model = lgb.train(params, train_data, num_boost_round=50, valid_sets=[val_data], early_stopping_rounds=10)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(model, out_path)
    print('Saved model to', out_path)


if __name__ == '__main__':
    train_and_save()
