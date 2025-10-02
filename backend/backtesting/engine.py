"""
Backtesting engine for Hermes.

Exposes run_backtest(symbol: str, start_date: str, end_date: str)
which fetches historical data, calls the AI agent for each candle, simulates
trades using fixed-fraction sizing, and returns metrics and an equity curve.

Thoroughly commented for later tweaks to risk management and trading rules.
"""
from __future__ import annotations

import csv
import math
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
import yfinance as yf

from ..agent import TradingAgent, TradingPrediction, Signal
from .. import db as _db  # ensure DB helpers available

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'backtests.db')


@dataclass
class TradeRecord:
    entry_date: datetime
    exit_date: Optional[datetime]
    symbol: str
    action: str  # BUY/SELL
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    pnl: Optional[float]
    pct_return: Optional[float]


def _ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS backtests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            start_date TEXT,
            end_date TEXT,
            initial_balance REAL,
            final_balance REAL,
            metrics_json TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backtest_id INTEGER,
            entry_date TEXT,
            exit_date TEXT,
            symbol TEXT,
            action TEXT,
            entry_price REAL,
            exit_price REAL,
            quantity REAL,
            pnl REAL,
            pct_return REAL
        )
        """
    )
    conn.commit()
    conn.close()


def _save_backtest_result(symbol: str, start: str, end: str, initial_balance: float, final_balance: float, metrics: Dict[str, Any], trades: List[TradeRecord]) -> int:
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO backtests (symbol, start_date, end_date, initial_balance, final_balance, metrics_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (symbol, start, end, initial_balance, final_balance, str(metrics), datetime.utcnow().isoformat()),
    )
    backtest_id = cur.lastrowid
    for t in trades:
        cur.execute(
            "INSERT INTO trades (backtest_id, entry_date, exit_date, symbol, action, entry_price, exit_price, quantity, pnl, pct_return) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                backtest_id,
                t.entry_date.isoformat(),
                t.exit_date.isoformat() if t.exit_date else None,
                t.symbol,
                t.action,
                t.entry_price,
                t.exit_price,
                t.quantity,
                t.pnl,
                t.pct_return,
            ),
        )
    conn.commit()
    conn.close()
    return backtest_id


def _export_trades_csv(trades: List[TradeRecord], csv_path: str):
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['entry_date', 'exit_date', 'symbol', 'action', 'entry_price', 'exit_price', 'quantity', 'pnl', 'pct_return'])
        for t in trades:
            writer.writerow([
                t.entry_date.isoformat(),
                t.exit_date.isoformat() if t.exit_date else '',
                t.symbol,
                t.action,
                t.entry_price,
                t.exit_price if t.exit_price else '',
                t.quantity,
                t.pnl if t.pnl is not None else '',
                t.pct_return if t.pct_return is not None else '',
            ])


def run_backtest(symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Run a backtest using the AI trading agent.

    Args:
        symbol: Ticker symbol (e.g., 'AAPL', 'BTC-USD')
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD

    Returns:
        Dictionary with metrics and equity curve and backtest_id
    """
    # Basic parameters
    initial_balance = 10_000.0
    balance = initial_balance
    equity_curve: List[Tuple[str, float]] = []  # date, portfolio_value
    trades: List[TradeRecord] = []

    # Risk management
    risk_percent = 0.02  # 2% of account per trade (fixed fractional)

    # Fetch historical daily data
    df = yf.download(symbol, start=start_date, end=end_date, progress=False)
    if df.empty:
        raise ValueError(f"No historical data for {symbol} between {start_date} and {end_date}")

    # Ensure index is datetime and sorted ascending
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    agent = TradingAgent()

    # Position tracking
    position_open = False
    position_entry_price = 0.0
    position_quantity = 0.0
    position_entry_date: Optional[datetime] = None

    # For Sharpe calculation, track daily returns
    daily_portfolio_values: List[float] = []

    for date, row in df.iterrows():
        # For each daily candle, ask the AI agent for a prediction
        # The agent expects symbol/timeframe; we'll use '1d' timeframe
        prediction: Optional[TradingPrediction] = None
        try:
            # agent.analyze_asset is async in original; call synchronously via .analyze_asset
            # If TradingAgent.analyze_asset is async, call using asyncio.run may be heavy; many agents will provide sync fallback
            import asyncio
            prediction = asyncio.run(agent.analyze_asset(symbol, '1d'))
        except Exception:
            # If async call fails inside sync context, fallback to agent._generate_fallback_prediction
            market_data = agent.market_fetcher.fetch_market_data(symbol, timeframe='1d')
            # Can't await here—use fallback prediction based on last known data
            prediction = agent._generate_fallback_prediction(agent.market_fetcher.fetch_market_data.__self__ if False else type('md', (), {'symbol': symbol, 'current_price': row['Close'], 'technical_indicators': {}, 'volume_profile': {'avg_volume': row['Volume'], 'current_volume': row['Volume'], 'volume_ratio': 1}, 'volatility': 0.0, 'ohlcv': df}), None, '1d')

        price = float(row['Close'])

        # If there is an open position, check stop-loss/target or SELL signal
        if position_open:
            exit_reason = None
            exit_price = price

            # Respect stop-loss/target if provided
            if prediction.stop_loss and price <= prediction.stop_loss:
                exit_reason = 'stop_loss'
            elif prediction.target_price and price >= prediction.target_price:
                exit_reason = 'target'
            elif prediction.signal == Signal.SELL:
                exit_reason = 'sell_signal'

            if exit_reason:
                # Close position
                pnl = (exit_price - position_entry_price) * position_quantity
                pct = pnl / (position_entry_price * position_quantity) if position_entry_price * position_quantity != 0 else 0
                trade = TradeRecord(
                    entry_date=position_entry_date,
                    exit_date=pd.to_datetime(date).to_pydatetime(),
                    symbol=symbol,
                    action='SELL',
                    entry_price=position_entry_price,
                    exit_price=exit_price,
                    quantity=position_quantity,
                    pnl=pnl,
                    pct_return=pct * 100,
                )
                trades.append(trade)
                balance += pnl
                position_open = False
                position_entry_price = 0.0
                position_quantity = 0.0
                position_entry_date = None

        # If no position open and signal is BUY, enter a new position according to risk sizing
        if not position_open and prediction.signal == Signal.BUY:
            # Determine risk per share if stop_loss available; otherwise assume 2% of price
            if prediction.stop_loss and prediction.stop_loss < price:
                risk_per_share = price - prediction.stop_loss
            else:
                # fallback to a small fraction of price as risk per share
                risk_per_share = price * 0.02

            # Maximum dollar risk per trade
            max_risk = balance * risk_percent
            if risk_per_share <= 0:
                # Avoid division by zero or negative risk
                continue
            qty = math.floor(max_risk / risk_per_share)
            if qty <= 0:
                # Can't take a position due to small balance
                continue

            position_open = True
            position_entry_price = price
            position_quantity = qty
            position_entry_date = pd.to_datetime(date).to_pydatetime()

            # Record entry trade with no exit yet
            trade = TradeRecord(
                entry_date=position_entry_date,
                exit_date=None,
                symbol=symbol,
                action='BUY',
                entry_price=position_entry_price,
                exit_price=None,
                quantity=position_quantity,
                pnl=None,
                pct_return=None,
            )
            trades.append(trade)

        # Update daily portfolio value
        position_value = position_quantity * price if position_open else 0.0
        portfolio_value = balance + position_value
        equity_curve.append((pd.to_datetime(date).strftime('%Y-%m-%d'), portfolio_value))
        daily_portfolio_values.append(portfolio_value)

    # At the end, if a position is still open, close at last price
    if position_open:
        last_price = float(df['Close'].iloc[-1])
        pnl = (last_price - position_entry_price) * position_quantity
        pct = pnl / (position_entry_price * position_quantity) if position_entry_price * position_quantity != 0 else 0
        trade = TradeRecord(
            entry_date=position_entry_date,
            exit_date=pd.to_datetime(df.index[-1]).to_pydatetime(),
            symbol=symbol,
            action='SELL',
            entry_price=position_entry_price,
            exit_price=last_price,
            quantity=position_quantity,
            pnl=pnl,
            pct_return=pct * 100,
        )
        trades.append(trade)
        balance += pnl

    final_balance = balance

    # Metrics calculation
    returns = np.diff(daily_portfolio_values) / np.array(daily_portfolio_values[:-1]) if len(daily_portfolio_values) > 1 else np.array([])
    total_return_pct = (final_balance / initial_balance - 1.0) * 100.0
    win_trades = [t for t in trades if t.pnl is not None and t.pnl > 0]
    win_rate = (len(win_trades) / len([t for t in trades if t.pnl is not None])) * 100.0 if any(t.pnl is not None for t in trades) else 0.0

    # Max drawdown
    series = np.array(daily_portfolio_values)
    if series.size > 0:
        peaks = np.maximum.accumulate(series)
        drawdowns = (peaks - series) / peaks
        max_drawdown = np.max(drawdowns) * 100.0
    else:
        max_drawdown = 0.0

    # Sharpe ratio using daily returns (assume risk-free = 0)
    if returns.size > 1 and np.std(returns, ddof=1) != 0:
        sharpe = (np.mean(returns) / np.std(returns, ddof=1)) * math.sqrt(252)
    else:
        sharpe = 0.0

    metrics = {
        'initial_balance': initial_balance,
        'final_balance': final_balance,
        'total_return_pct': total_return_pct,
        'win_rate_pct': win_rate,
        'max_drawdown_pct': max_drawdown,
        'sharpe_ratio': sharpe,
        'trades': len([t for t in trades if t.pnl is not None])
    }

    # Save results and return
    backtest_id = _save_backtest_result(symbol, start_date, end_date, initial_balance, final_balance, metrics, trades)

    # Write CSV to a temp path
    csv_path = os.path.join(os.path.dirname(DB_PATH), f'backtest_{backtest_id}_trades.csv')
    _export_trades_csv(trades, csv_path)

    return {
        'backtest_id': backtest_id,
        'metrics': metrics,
        'equity_curve': [{'date': d, 'value': v} for d, v in equity_curve],
        'csv_path': csv_path,
    }
