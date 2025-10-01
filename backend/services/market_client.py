"""Market data fetching adapters (Binance, AlphaVantage, yfinance).

This module provides a simple yfinance-backed adapter. The function is async
but uses asyncio.to_thread to call the synchronous yfinance API so it won't
block the event loop.
"""
import asyncio
from typing import Optional
import pandas as pd


async def fetch_candles(symbol: str, tf: str = '1m') -> pd.DataFrame:
    """Fetch recent candles for a symbol and return as a pandas DataFrame.

    Uses yfinance under the hood. Returns a dataframe with columns:
    ['timestamp','open','high','low','close','volume']
    """
    # Map timeframe to yfinance interval
    tf_map = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '1h': '60m',
        '1d': '1d',
    }
    interval = tf_map.get(tf, tf)

    # Choose a reasonable period for fetching based on interval
    if interval.endswith('m') and interval != '60m':
        period = '7d'
    elif interval == '60m':
        period = '60d'
    else:
        period = '120d'

    # Synchronous yfinance call wrapped in thread
    def _download():
        import yfinance as yf

        try:
            data = yf.download(
                tickers=symbol,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=False,
            )
        except Exception:
            return pd.DataFrame()

        if data is None or data.empty:
            return pd.DataFrame()

        # yfinance returns a DataFrame with DatetimeIndex and OHLCV columns
        df = data.reset_index()

        # Normalize column names (be permissive to case/label variations)
        col_map = {}
        for c in df.columns:
            lc = str(c).lower()
            if 'date' in lc or 'datetime' in lc or lc == 'index':
                col_map[c] = 'timestamp'
            elif lc in ('open', 'open_'):
                col_map[c] = 'open'
            elif lc in ('high', 'high_'):
                col_map[c] = 'high'
            elif lc in ('low', 'low_'):
                col_map[c] = 'low'
            elif lc in ('close', 'close_') or 'adj' in lc and 'close' in lc:
                col_map[c] = 'close'
            elif 'volume' in lc:
                col_map[c] = 'volume'

        if col_map:
            df = df.rename(columns=col_map)

        # Find close column: if not present, try common alternates
        if 'close' not in df.columns:
            # try 'Adj Close' or 'Adj_Close' raw names
            for alt in ['Adj Close', 'Adj_Close', 'adj_close', 'Close']:
                if alt in df.columns:
                    df = df.rename(columns={alt: 'close'})
                    break

        if 'close' not in df.columns:
            # No usable close column — return empty result to trigger fallback
            return pd.DataFrame()

        # Ensure other required columns exist
        for col in ['timestamp', 'open', 'high', 'low', 'volume']:
            if col not in df.columns:
                df[col] = None

        # Convert timestamp to naive datetime where possible
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        except Exception:
            # leave as-is if conversion fails
            pass

        # Keep relevant columns and drop rows with no close
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        df = df.dropna(subset=['close'])
        return df

    df = await asyncio.to_thread(_download)
    return df
