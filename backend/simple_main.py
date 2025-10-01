from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import asyncio
try:
    # prefer package-relative import when running as module (backend.simple_main)
    from .services.redis_client import get_redis_status
except Exception:
    try:
        # fallback for running directly (python simple_main.py)
        from services.redis_client import get_redis_status
    except Exception:
        # provide a safe async fallback so health_check can always run
        async def get_redis_status():
            return {'available': False}
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Trading Companion API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register admin router
try:
    try:
        from routers.admin import router as admin_router
    except Exception:
        from backend.routers.admin import router as admin_router
    app.include_router(admin_router)
except Exception:
    pass
# include agent router so /api/agent/* endpoints are available when running this simple_main app
try:
    try:
        from routers import agent as agent_mod
        app.include_router(agent_mod.router, prefix='/api')
    except Exception:
        from backend.routers import agent as agent_mod
        app.include_router(agent_mod.router, prefix='/api')
except Exception:
    # If agent router can't be included, log but continue so other endpoints remain available
    import logging
    logging.getLogger(__name__).warning('Agent router could not be included in simple_main')

# include semantic router for retrieval/vector store
try:
    try:
        from routers.semantic import router as semantic_router
        app.include_router(semantic_router, prefix='/api')
    except Exception:
        from backend.routers.semantic import router as semantic_router
        app.include_router(semantic_router, prefix='/api')
except Exception:
    logging.getLogger(__name__).warning('Semantic router could not be included in simple_main')

# include background router for long-running responses
try:
    try:
        from routers.background_router import router as bg_router
        app.include_router(bg_router, prefix='/api')
    except Exception:
        from backend.routers.background_router import router as bg_router
        app.include_router(bg_router, prefix='/api')
except Exception:
    logging.getLogger(__name__).warning('Background router could not be included in simple_main')

# include visualization router for agent graphs
try:
    try:
        from routers.visualization import router as viz_router
        app.include_router(viz_router, prefix='/api')
    except Exception:
        from backend.routers.visualization import router as viz_router
        app.include_router(viz_router, prefix='/api')
except Exception:
    logging.getLogger(__name__).warning('Visualization router could not be included in simple_main')

@app.get("/health")
async def health_check():
    redis_status = {
        'available': False
    }
    try:
        # attempt to get redis status but don't fail if redis client isn't installed
        redis_status = await get_redis_status()
    except Exception:
        redis_status = {'available': False}

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "redis": redis_status,
        "finbert_available": getattr(app.state, 'finbert_available', False),
    }


@app.on_event('startup')
async def check_optional_components():
    # FinBERT availability
    try:
        from services.finbert import load_finbert  # noqa: F401
        app.state.finbert_available = True
        logger.info('FinBERT support available')
    except Exception:
        app.state.finbert_available = False
        logger.info('FinBERT support not available')
    # Optionally wait for external services (Postgres/Redis) and initialize DB.
    # Set WAIT_FOR_SERVICES=1 in environment to enable. This uses the helper
    # script at backend/scripts/wait_for_services.py when available.
    try:
        import os
        if os.getenv('WAIT_FOR_SERVICES'):
            try:
                # import as module when running the package
                from backend.scripts.wait_for_services import main as wait_main
            except Exception:
                try:
                    # fallback when running from backend/ directly
                    from scripts.wait_for_services import main as wait_main
                except Exception:
                    wait_main = None
            if wait_main:
                logger.info('WAIT_FOR_SERVICES set — waiting for dependent services')
                # run the blocking wait in a thread to avoid blocking the event loop
                import asyncio
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, wait_main)
            else:
                logger.warning('wait_for_services helper not found; skipping')
    except Exception as e:
        logger.warning('Error while attempting wait_for_services: %s', e)

@app.get("/assets/categories")
async def get_asset_categories():
    """Get all available asset categories"""
    return {
        "categories": [
            {"key": "crypto", "name": "Cryptocurrency", "count": 10},
            {"key": "forex", "name": "Foreign Exchange", "count": 8},
            {"key": "stocks", "name": "Stocks", "count": 15},
            {"key": "commodities", "name": "Commodities", "count": 12},
            {"key": "indices", "name": "Market Indices", "count": 8}
        ]
    }

@app.get("/assets/search")
async def search_assets():
    """Search for assets by query and/or category"""
    return {
        "assets": [
            {"symbol": "BTCUSDT", "name": "Bitcoin", "category": "crypto", "exchange": "Binance", "description": "Bitcoin to USDT"},
            {"symbol": "ETHUSD", "name": "Ethereum", "category": "crypto", "exchange": "Binance", "description": "Ethereum to USD"},
            {"symbol": "EURUSD", "name": "EUR/USD", "category": "forex", "exchange": "Forex", "description": "Euro to US Dollar"},
            {"symbol": "GOLD", "name": "Gold", "category": "commodities", "exchange": "COMEX", "description": "Gold Futures"},
            {"symbol": "SPY", "name": "S&P 500 ETF", "category": "stocks", "exchange": "NYSE", "description": "SPDR S&P 500 ETF"}
        ],
        "count": 5
    }

@app.get("/market/{symbol}/current")
async def get_current_price(symbol: str):
    """Get current market data for an asset"""
    # Mock data for demo
    mock_prices = {
        "BTCUSDT": 43000.50,
        "ETHUSD": 2800.25,
        "EURUSD": 1.0850,
        "GOLD": 2050.75,
        "SPY": 485.20
    }
    
    price = mock_prices.get(symbol, 100.00)
    
    return {
        "symbol": symbol,
        "price": price,
        "change_24h": price * 0.02,  # Mock 2% change
        "change_percent_24h": 2.0,
        "volume_24h": 1000000,
        "market_cap": None,
        "high_24h": price * 1.05,
        "low_24h": price * 0.95,
        "last_updated": datetime.now().isoformat()
    }

@app.post("/predictions/generate")
async def generate_prediction():
    """Generate AI trading prediction for an asset"""
    return {
        "symbol": "BTCUSDT",
        "signal": "BUY",
        "confidence": 78.5,
        "entry_price": 43000.50,
        "target_price": 45000.00,
        "stop_loss": 41000.00,
        "reasoning": ["Technical indicators show bullish momentum", "Market sentiment is positive"],
        "timestamp": datetime.now().isoformat(),
        "recommendation": "Consider buying with high confidence. Target: $45000.00, Stop Loss: $41000.00"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
