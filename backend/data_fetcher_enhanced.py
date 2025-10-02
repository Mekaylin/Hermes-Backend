"""
Multi-source data fetcher for trading data
Supports Binance, Yahoo Finance, and Alpha Vantage APIs
"""

import aiohttp
import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import yfinance as yf

from .assets import Asset, AssetCategory

logger = logging.getLogger(__name__)

@dataclass
class OHLCV:
    """Open, High, Low, Close, Volume data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str

@dataclass
class MarketData:
    """Complete market data for an asset"""
    asset: Asset
    current_price: float
    price_change_24h: float
    price_change_pct_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    ohlcv_data: List[OHLCV]
    last_updated: datetime

    # Backwards-compatible properties expected by other modules
    @property
    def price(self) -> float:
        return float(self.current_price)

    @property
    def change_24h(self) -> float:
        return float(self.price_change_24h)

    @property
    def change_percent_24h(self) -> float:
        return float(self.price_change_pct_24h)

    @property
    def market_cap(self):
        # Not provided by all sources; return None when unavailable
        return getattr(self, "_market_cap", None)

class DataFetcher:
    """Multi-source data fetcher with fallback mechanisms"""
    
    def __init__(self, alpha_vantage_key: Optional[str] = None):
        self.alpha_vantage_key = alpha_vantage_key
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_crypto_data(self, asset: Asset, period: str = "1d", interval: str = "1h") -> Optional[MarketData]:
        """Fetch cryptocurrency data from Binance API"""
        try:
            base_url = "https://api.binance.com/api/v3"
            
            # Get 24hr ticker statistics
            ticker_url = f"{base_url}/ticker/24hr?symbol={asset.api_symbol}"
            
            async with self.session.get(ticker_url) as response:
                if response.status != 200:
                    logger.error(f"Binance API error for {asset.symbol}: {response.status}")
                    return None
                    
                ticker_data = await response.json()
            
            # Get kline/candlestick data
            klines_url = f"{base_url}/klines?symbol={asset.api_symbol}&interval={interval}&limit=100"
            
            async with self.session.get(klines_url) as response:
                if response.status != 200:
                    logger.error(f"Binance klines API error for {asset.symbol}: {response.status}")
                    return None
                    
                klines_data = await response.json()
            
            # Parse OHLCV data
            ohlcv_data = []
            for kline in klines_data:
                ohlcv_data.append(OHLCV(
                    timestamp=datetime.fromtimestamp(kline[0] / 1000),
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5]),
                    symbol=asset.symbol
                ))
            
            return MarketData(
                asset=asset,
                current_price=float(ticker_data['lastPrice']),
                price_change_24h=float(ticker_data['priceChange']),
                price_change_pct_24h=float(ticker_data['priceChangePercent']),
                volume_24h=float(ticker_data['volume']),
                high_24h=float(ticker_data['highPrice']),
                low_24h=float(ticker_data['lowPrice']),
                ohlcv_data=ohlcv_data,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching crypto data for {asset.symbol}: {e}")
            return None
    
    async def fetch_stock_data(self, asset: Asset, period: str = "5d", interval: str = "1h") -> Optional[MarketData]:
        """Fetch stock/forex/commodity data from Yahoo Finance"""
        try:
            # Use yfinance for stock data (runs in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, asset.api_symbol)
            
            # Get historical data
            hist = await loop.run_in_executor(
                None, 
                lambda: ticker.history(period=period, interval=interval)
            )
            
            if hist.empty:
                logger.error(f"No historical data found for {asset.symbol}")
                return None
            
            # Get current info
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            # Parse OHLCV data
            ohlcv_data = []
            for timestamp, row in hist.iterrows():
                # Ensure we convert whatever index type (Timestamp, numpy datetime64, etc.)
                # to a Python datetime safely for downstream usage and to satisfy
                # the language server (pylance) which may view the index as Hashable.
                ts_dt = pd.to_datetime(timestamp).to_pydatetime()
                ohlcv_data.append(OHLCV(
                    timestamp=ts_dt,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume']),
                    symbol=asset.symbol
                ))
            
            current_price = hist['Close'][-1]
            prev_close = hist['Close'][-2] if len(hist) > 1 else current_price
            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close) * 100 if prev_close != 0 else 0
            
            return MarketData(
                asset=asset,
                current_price=float(current_price),
                price_change_24h=float(price_change),
                price_change_pct_24h=float(price_change_pct),
                volume_24h=float(hist['Volume'][-1]),
                high_24h=float(hist['High'].max()),
                low_24h=float(hist['Low'].min()),
                ohlcv_data=ohlcv_data,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {asset.symbol}: {e}")
            return None
    
    async def fetch_alpha_vantage_data(self, asset: Asset, function: str = "TIME_SERIES_INTRADAY") -> Optional[MarketData]:
        """Fetch data from Alpha Vantage API (backup/premium data source)"""
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not provided")
            return None
            
        try:
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": function,
                "symbol": asset.api_symbol,
                "interval": "60min",
                "apikey": self.alpha_vantage_key,
                "outputsize": "compact"
            }
            
            async with self.session.get(base_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Alpha Vantage API error for {asset.symbol}: {response.status}")
                    return None
                    
                data = await response.json()
            
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return None
                
            if "Note" in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            # Parse time series data
            time_series_key = None
            for key in data.keys():
                if "Time Series" in key:
                    time_series_key = key
                    break
            
            if not time_series_key:
                logger.error(f"No time series data found for {asset.symbol}")
                return None
            
            time_series = data[time_series_key]
            ohlcv_data = []
            
            for timestamp_str, values in time_series.items():
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                ohlcv_data.append(OHLCV(
                    timestamp=timestamp,
                    open=float(values["1. open"]),
                    high=float(values["2. high"]),
                    low=float(values["3. low"]),
                    close=float(values["4. close"]),
                    volume=float(values["5. volume"]),
                    symbol=asset.symbol
                ))
            
            # Sort by timestamp
            ohlcv_data.sort(key=lambda x: x.timestamp)
            
            if not ohlcv_data:
                logger.error(f"No OHLCV data parsed for {asset.symbol}")
                return None
            
            current = ohlcv_data[-1]
            previous = ohlcv_data[-2] if len(ohlcv_data) > 1 else current
            
            price_change = current.close - previous.close
            price_change_pct = (price_change / previous.close) * 100 if previous.close != 0 else 0
            
            return MarketData(
                asset=asset,
                current_price=current.close,
                price_change_24h=price_change,
                price_change_pct_24h=price_change_pct,
                volume_24h=sum([point.volume for point in ohlcv_data[-24:]]),  # Last 24 hours
                high_24h=max([point.high for point in ohlcv_data[-24:]]),
                low_24h=min([point.low for point in ohlcv_data[-24:]]),
                ohlcv_data=ohlcv_data,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data for {asset.symbol}: {e}")
            return None
    
    async def fetch_market_data(self, asset: Asset) -> Optional[MarketData]:
        """Fetch market data with fallback strategy based on asset category"""
        
        # Route to appropriate data source based on asset category
        if asset.category == AssetCategory.CRYPTO:
            data = await self.fetch_crypto_data(asset)
            if data:
                return data
        
        # Try Yahoo Finance for stocks, forex, commodities, indices
        if asset.category in [AssetCategory.STOCKS, AssetCategory.FOREX, 
                             AssetCategory.COMMODITIES, AssetCategory.INDICES]:
            data = await self.fetch_stock_data(asset)
            if data:
                return data
        
        # Fallback to Alpha Vantage if available
        if self.alpha_vantage_key:
            data = await self.fetch_alpha_vantage_data(asset)
            if data:
                return data
        
        logger.error(f"Unable to fetch data for {asset.symbol} from any source")
        return None

    # Backwards-compatible convenience wrappers used elsewhere in the codebase
    async def get_market_data(self, symbol_or_asset) -> Optional[MarketData]:
        """Accept either an Asset instance or a symbol string and return MarketData"""
        # If a symbol string was passed, try to resolve via AssetManager lazily to avoid circular imports
        if isinstance(symbol_or_asset, str):
            try:
                from .assets import AssetManager
                asset = AssetManager.get_asset_by_symbol(symbol_or_asset)
            except Exception:
                asset = None
        else:
            asset = symbol_or_asset

        if not asset:
            return None

        return await self.fetch_market_data(asset)

    async def get_ohlcv_data(self, symbol_or_asset, timeframe: str = "1h", limit: int = 100) -> Optional[List[OHLCV]]:
        """Return raw OHLCV list for a given symbol or Asset"""
        if isinstance(symbol_or_asset, str):
            try:
                from .assets import AssetManager
                asset = AssetManager.get_asset_by_symbol(symbol_or_asset)
            except Exception:
                asset = None
        else:
            asset = symbol_or_asset

        if not asset:
            return None

        # Prefer crypto for binance-style assets if category indicates crypto
        data = await self.fetch_market_data(asset)
        if data:
            return data.ohlcv_data

        return None
    
    async def fetch_multiple_assets(self, assets: List[Asset]) -> Dict[str, MarketData]:
        """Fetch data for multiple assets concurrently"""
        tasks = [self.fetch_market_data(asset) for asset in assets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        market_data = {}
        for asset, result in zip(assets, results):
            if isinstance(result, MarketData):
                market_data[asset.symbol] = result
            elif isinstance(result, Exception):
                logger.error(f"Error fetching data for {asset.symbol}: {result}")
        
        return market_data

# Utility functions for data processing
def ohlcv_to_dataframe(ohlcv_data: List[OHLCV]) -> pd.DataFrame:
    """Convert OHLCV data to pandas DataFrame"""
    data = {
        'timestamp': [point.timestamp for point in ohlcv_data],
        'open': [point.open for point in ohlcv_data],
        'high': [point.high for point in ohlcv_data],
        'low': [point.low for point in ohlcv_data],
        'close': [point.close for point in ohlcv_data],
        'volume': [point.volume for point in ohlcv_data],
    }
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df

def calculate_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate basic technical indicators"""
    # Simple Moving Averages
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # Exponential Moving Averages
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()
    
    # MACD
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    return df
