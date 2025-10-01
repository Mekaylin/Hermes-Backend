"""
Asset Configuration and Management
Defines all tradeable asset categories and their specific symbols
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

class AssetCategory(str, Enum):
    FOREX = "forex"
    COMMODITIES = "commodities" 
    STOCKS = "stocks"
    INDICES = "indices"
    CRYPTO = "crypto"

@dataclass
class Asset:
    symbol: str
    name: str
    category: AssetCategory
    exchange: str
    api_symbol: str  # Symbol format for API calls
    description: str = ""
    min_price_change: float = 0.0001
    
class AssetManager:
    """Manages all available assets across different categories"""
    
    ASSETS: Dict[AssetCategory, List[Asset]] = {
        AssetCategory.FOREX: [
            Asset("EUR/USD", "Euro/US Dollar", AssetCategory.FOREX, "forex", "EURUSD=X", "Major currency pair"),
            Asset("GBP/USD", "British Pound/US Dollar", AssetCategory.FOREX, "forex", "GBPUSD=X", "Cable"),
            Asset("USD/JPY", "US Dollar/Japanese Yen", AssetCategory.FOREX, "forex", "USDJPY=X", "Major Asian pair"),
            Asset("AUD/USD", "Australian Dollar/US Dollar", AssetCategory.FOREX, "forex", "AUDUSD=X", "Aussie"),
            Asset("USD/CAD", "US Dollar/Canadian Dollar", AssetCategory.FOREX, "forex", "USDCAD=X", "Loonie"),
            Asset("USD/CHF", "US Dollar/Swiss Franc", AssetCategory.FOREX, "forex", "USDCHF=X", "Swissie"),
            Asset("NZD/USD", "New Zealand Dollar/US Dollar", AssetCategory.FOREX, "forex", "NZDUSD=X", "Kiwi"),
            Asset("EUR/GBP", "Euro/British Pound", AssetCategory.FOREX, "forex", "EURGBP=X", "Cross pair"),
            Asset("EUR/JPY", "Euro/Japanese Yen", AssetCategory.FOREX, "forex", "EURJPY=X", "Cross pair"),
            Asset("GBP/JPY", "British Pound/Japanese Yen", AssetCategory.FOREX, "forex", "GBPJPY=X", "Cross pair"),
        ],
        
        AssetCategory.COMMODITIES: [
            Asset("GOLD", "Gold", AssetCategory.COMMODITIES, "commodity", "GC=F", "Precious metal"),
            Asset("SILVER", "Silver", AssetCategory.COMMODITIES, "commodity", "SI=F", "Precious metal"),
            Asset("OIL", "Crude Oil", AssetCategory.COMMODITIES, "commodity", "CL=F", "WTI Crude Oil"),
            Asset("BRENT", "Brent Oil", AssetCategory.COMMODITIES, "commodity", "BZ=F", "Brent Crude Oil"),
            Asset("NATGAS", "Natural Gas", AssetCategory.COMMODITIES, "commodity", "NG=F", "Energy commodity"),
            Asset("COPPER", "Copper", AssetCategory.COMMODITIES, "commodity", "HG=F", "Industrial metal"),
            Asset("PLATINUM", "Platinum", AssetCategory.COMMODITIES, "commodity", "PL=F", "Precious metal"),
            Asset("PALLADIUM", "Palladium", AssetCategory.COMMODITIES, "commodity", "PA=F", "Precious metal"),
            Asset("WHEAT", "Wheat", AssetCategory.COMMODITIES, "commodity", "ZW=F", "Agricultural"),
            Asset("CORN", "Corn", AssetCategory.COMMODITIES, "commodity", "ZC=F", "Agricultural"),
        ],
        
        AssetCategory.STOCKS: [
            Asset("AAPL", "Apple Inc.", AssetCategory.STOCKS, "nasdaq", "AAPL", "Technology company"),
            Asset("MSFT", "Microsoft Corporation", AssetCategory.STOCKS, "nasdaq", "MSFT", "Technology company"),
            Asset("GOOGL", "Alphabet Inc.", AssetCategory.STOCKS, "nasdaq", "GOOGL", "Technology company"),
            Asset("AMZN", "Amazon.com Inc.", AssetCategory.STOCKS, "nasdaq", "AMZN", "E-commerce giant"),
            Asset("TSLA", "Tesla Inc.", AssetCategory.STOCKS, "nasdaq", "TSLA", "Electric vehicles"),
            Asset("NVDA", "NVIDIA Corporation", AssetCategory.STOCKS, "nasdaq", "NVDA", "Semiconductor company"),
            Asset("META", "Meta Platforms Inc.", AssetCategory.STOCKS, "nasdaq", "META", "Social media"),
            Asset("NFLX", "Netflix Inc.", AssetCategory.STOCKS, "nasdaq", "NFLX", "Streaming service"),
            Asset("AMD", "Advanced Micro Devices", AssetCategory.STOCKS, "nasdaq", "AMD", "Semiconductor company"),
            Asset("PYPL", "PayPal Holdings Inc.", AssetCategory.STOCKS, "nasdaq", "PYPL", "Digital payments"),
            Asset("JPM", "JPMorgan Chase & Co.", AssetCategory.STOCKS, "nyse", "JPM", "Investment bank"),
            Asset("JNJ", "Johnson & Johnson", AssetCategory.STOCKS, "nyse", "JNJ", "Healthcare"),
            Asset("V", "Visa Inc.", AssetCategory.STOCKS, "nyse", "V", "Payment processing"),
            Asset("PG", "Procter & Gamble", AssetCategory.STOCKS, "nyse", "PG", "Consumer goods"),
            Asset("DIS", "The Walt Disney Company", AssetCategory.STOCKS, "nyse", "DIS", "Entertainment"),
        ],
        
        AssetCategory.INDICES: [
            Asset("SPX", "S&P 500", AssetCategory.INDICES, "index", "^GSPC", "US large-cap index"),
            Asset("NDX", "NASDAQ 100", AssetCategory.INDICES, "index", "^NDX", "US tech-heavy index"),
            Asset("DJI", "Dow Jones Industrial Average", AssetCategory.INDICES, "index", "^DJI", "US blue-chip index"),
            Asset("RUT", "Russell 2000", AssetCategory.INDICES, "index", "^RUT", "US small-cap index"),
            Asset("VIX", "CBOE Volatility Index", AssetCategory.INDICES, "index", "^VIX", "Fear index"),
            Asset("FTSE", "FTSE 100", AssetCategory.INDICES, "index", "^FTSE", "UK main index"),
            Asset("DAX", "DAX", AssetCategory.INDICES, "index", "^GDAXI", "German main index"),
            Asset("CAC", "CAC 40", AssetCategory.INDICES, "index", "^FCHI", "French main index"),
            Asset("NIKKEI", "Nikkei 225", AssetCategory.INDICES, "index", "^N225", "Japanese main index"),
            Asset("HSI", "Hang Seng Index", AssetCategory.INDICES, "index", "^HSI", "Hong Kong main index"),
        ],
        
        AssetCategory.CRYPTO: [
            Asset("BTC/USDT", "Bitcoin", AssetCategory.CRYPTO, "binance", "BTCUSDT", "Digital gold"),
            Asset("ETH/USDT", "Ethereum", AssetCategory.CRYPTO, "binance", "ETHUSDT", "Smart contracts platform"),
            Asset("BNB/USDT", "Binance Coin", AssetCategory.CRYPTO, "binance", "BNBUSDT", "Exchange token"),
            Asset("ADA/USDT", "Cardano", AssetCategory.CRYPTO, "binance", "ADAUSDT", "Proof-of-stake blockchain"),
            Asset("SOL/USDT", "Solana", AssetCategory.CRYPTO, "binance", "SOLUSDT", "High-performance blockchain"),
            Asset("XRP/USDT", "Ripple", AssetCategory.CRYPTO, "binance", "XRPUSDT", "Digital payment protocol"),
            Asset("DOT/USDT", "Polkadot", AssetCategory.CRYPTO, "binance", "DOTUSDT", "Multi-chain protocol"),
            Asset("DOGE/USDT", "Dogecoin", AssetCategory.CRYPTO, "binance", "DOGEUSDT", "Meme cryptocurrency"),
            Asset("AVAX/USDT", "Avalanche", AssetCategory.CRYPTO, "binance", "AVAXUSDT", "Smart contracts platform"),
            Asset("MATIC/USDT", "Polygon", AssetCategory.CRYPTO, "binance", "MATICUSDT", "Ethereum scaling solution"),
            Asset("LTC/USDT", "Litecoin", AssetCategory.CRYPTO, "binance", "LTCUSDT", "Digital silver"),
            Asset("UNI/USDT", "Uniswap", AssetCategory.CRYPTO, "binance", "UNIUSDT", "Decentralized exchange"),
        ]
    }
    
    @classmethod
    def get_assets_by_category(cls, category: AssetCategory) -> List[Asset]:
        """Get all assets for a specific category"""
        return cls.ASSETS.get(category, [])
    
    @classmethod
    def get_all_categories(cls) -> List[AssetCategory]:
        """Get all available asset categories"""
        return list(cls.ASSETS.keys())
    
    @classmethod
    def search_assets(cls, query: str, category: Optional[AssetCategory] = None) -> List[Asset]:
        """Search for assets by name or symbol"""
        query = query.lower()
        results = []
        
        categories_to_search = [category] if category else cls.get_all_categories()
        
        for cat in categories_to_search:
            for asset in cls.get_assets_by_category(cat):
                if (query in asset.symbol.lower() or 
                    query in asset.name.lower() or 
                    query in asset.description.lower()):
                    results.append(asset)
        
        return results
    
    @classmethod
    def get_asset_by_symbol(cls, symbol: str, category: Optional[AssetCategory] = None) -> Optional[Asset]:
        """Get specific asset by symbol"""
        categories_to_search = [category] if category else cls.get_all_categories()
        
        for cat in categories_to_search:
            for asset in cls.get_assets_by_category(cat):
                if asset.symbol == symbol or asset.api_symbol == symbol:
                    return asset
        
        return None
    
    @classmethod
    def get_popular_assets(cls, limit: int = 10) -> List[Asset]:
        """Get most popular assets across all categories"""
        popular = [
            # Most traded forex pairs
            cls.get_asset_by_symbol("EUR/USD"),
            cls.get_asset_by_symbol("GBP/USD"),
            cls.get_asset_by_symbol("USD/JPY"),
            
            # Major stocks
            cls.get_asset_by_symbol("AAPL"),
            cls.get_asset_by_symbol("TSLA"),
            cls.get_asset_by_symbol("NVDA"),
            
            # Key indices
            cls.get_asset_by_symbol("SPX"),
            cls.get_asset_by_symbol("NDX"),
            
            # Major crypto
            cls.get_asset_by_symbol("BTC/USDT"),
            cls.get_asset_by_symbol("ETH/USDT"),
            
            # Key commodities
            cls.get_asset_by_symbol("GOLD"),
            cls.get_asset_by_symbol("OIL"),
        ]
        
        # Filter out None values and limit results
        return [asset for asset in popular if asset is not None][:limit]
