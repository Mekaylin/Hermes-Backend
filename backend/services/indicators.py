"""Technical indicators computations using pandas and ta package."""
import pandas as pd
import numpy as np


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute EMA, RSI, MACD, Bollinger Bands, ATR and append as columns.

    Input df is expected to have columns: ['timestamp','open','high','low','close','volume']
    Returns df with additional indicator columns.
    """
    if df.empty:
        return df

    # Placeholder computations
    df = df.copy()
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['rsi_14'] = 50 + (df['close'].pct_change().fillna(0).rolling(window=14).mean() * 100)
    df['macd'] = df['ema_12'] - df['ema_26']
    df['bb_mid'] = df['close'].rolling(window=20).mean()
    df['bb_upper'] = df['bb_mid'] + 2 * df['close'].rolling(window=20).std()
    df['bb_lower'] = df['bb_mid'] - 2 * df['close'].rolling(window=20).std()
    df['atr'] = df['high'] - df['low']

    # Fill NA values for safety
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)
    df.fillna(0, inplace=True)

    return df
