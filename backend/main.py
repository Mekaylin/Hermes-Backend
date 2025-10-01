"""
FastAPI backend for trading companion app
Provides REST API and WebSocket support for real-time trading signals
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import uuid

from pydantic import BaseModel
from contextlib import asynccontextmanager

# Import our modules
from assets import AssetManager, Asset, AssetCategory
from data_fetcher_enhanced import DataFetcher

# ml_models may require native libs (lightgbm). Import lazily with a safe
# fallback so the app can start in degraded mode when LightGBM isn't present.
try:
    from ml_models import EnsemblePredictor, TradingSignal, SignalType
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import ml_models (proceeding with fallback): {e}")

    # Minimal fallback implementations
    from enum import Enum
    from dataclasses import dataclass
    import datetime

    class SignalType(Enum):
        BUY = "buy"
        SELL = "sell"
        HOLD = "hold"

    @dataclass
    class TradingSignal:
        signal: SignalType = SignalType.HOLD
        confidence: float = 50.0
        entry_price: float = 0.0
        target_price: float = 0.0
        stop_loss: float = 0.0
        reasoning: list = None
        timestamp: datetime.datetime = datetime.datetime.now()

    class EnsemblePredictor:
        def __init__(self):
            pass

        def predict(self, df):
            # Return a neutral HOLD signal when the real predictor is unavailable
            return TradingSignal()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
asset_manager = AssetManager()
data_fetcher = DataFetcher()
ml_predictor = EnsemblePredictor()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from subscriptions
        for symbol, connections in self.subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
    
    async def broadcast(self, message: dict):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection)
    
    async def send_to_subscribers(self, symbol: str, message: dict):
        if symbol in self.subscriptions:
            disconnected = []
            for connection in self.subscriptions[symbol]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.subscriptions[symbol].remove(connection)
    
    def subscribe(self, websocket: WebSocket, symbol: str):
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = []
        
        if websocket not in self.subscriptions[symbol]:
            self.subscriptions[symbol].append(websocket)
            logger.info(f"WebSocket subscribed to {symbol}")

manager = ConnectionManager()

# Background task for real-time data updates
class RealTimeDataManager:
    def __init__(self):
        self.active_symbols: set = set()
        self.update_interval = 30  # seconds
        self.is_running = False
    
    async def start(self):
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self.update_loop())
            logger.info("Real-time data manager started")
    
    async def stop(self):
        self.is_running = False
        logger.info("Real-time data manager stopped")
    
    async def add_symbol(self, symbol: str):
        self.active_symbols.add(symbol)
        logger.info(f"Added {symbol} to real-time updates")
    
    async def remove_symbol(self, symbol: str):
        self.active_symbols.discard(symbol)
        logger.info(f"Removed {symbol} from real-time updates")
    
    async def update_loop(self):
        while self.is_running:
            try:
                if self.active_symbols:
                    await self.update_all_symbols()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in real-time update loop: {e}")
    
    async def update_all_symbols(self):
        for symbol in self.active_symbols.copy():
            try:
                # Get latest market data
                market_data = await data_fetcher.get_market_data(symbol)
                
                if market_data:
                    # Send price update
                    price_update = {
                        "type": "price_update",
                        "symbol": symbol,
                        "price": market_data.price,
                        "change": market_data.change_24h,
                        "change_percent": market_data.change_percent_24h,
                        "volume": market_data.volume_24h,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await manager.send_to_subscribers(symbol, price_update)
                    
                    # Generate ML prediction if we have enough data
                    ohlcv_data = await data_fetcher.get_ohlcv_data(symbol, "1h", 100)
                    
                    if ohlcv_data and len(ohlcv_data) >= 50:
                        try:
                            # Convert to DataFrame for ML model
                            from data_fetcher_enhanced import ohlcv_to_dataframe
                            df = ohlcv_to_dataframe(ohlcv_data)
                            df['symbol'] = symbol
                            
                            # Generate trading signal
                            signal = ml_predictor.predict(df)
                            
                            signal_update = {
                                "type": "trading_signal",
                                "symbol": symbol,
                                "signal": signal.signal.value,
                                "confidence": signal.confidence,
                                "entry_price": signal.entry_price,
                                "target_price": signal.target_price,
                                "stop_loss": signal.stop_loss,
                                "reasoning": signal.reasoning,
                                "timestamp": signal.timestamp.isoformat()
                            }
                            
                            await manager.send_to_subscribers(symbol, signal_update)
                            
                        except Exception as e:
                            logger.error(f"Error generating ML prediction for {symbol}: {e}")
                
            except Exception as e:
                logger.error(f"Error updating {symbol}: {e}")

real_time_manager = RealTimeDataManager()

# Pydantic models for API
class AssetSearchRequest(BaseModel):
    query: Optional[str] = ""
    category: Optional[AssetCategory] = None
    limit: int = 50

class PredictionRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    periods: int = 100

class SubscriptionRequest(BaseModel):
    symbol: str
    action: str  # "subscribe" or "unsubscribe"

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting trading companion backend...")
    await real_time_manager.start()
    
    # Train ML models with sample data if available
    try:
        # You might want to train models with historical data here
        logger.info("ML models initialized (training would happen here with historical data)")
    except Exception as e:
        logger.error(f"Error initializing ML models: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down trading companion backend...")
    await real_time_manager.stop()

# Create FastAPI app
app = FastAPI(
    title="Trading Companion API",
    description="AI-powered trading analysis and signals for multiple asset classes",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Asset management endpoints
@app.get("/assets/categories")
async def get_asset_categories():
    """Get all available asset categories"""
    return {
        "categories": [
            {
                "key": category.value,
                "name": category.value.replace("_", " ").title(),
                "count": len(asset_manager.get_assets_by_category(category))
            }
            for category in AssetCategory
        ]
    }

@app.post("/assets/search")
async def search_assets(request: AssetSearchRequest):
    """Search for assets by query and/or category"""
    try:
        assets = asset_manager.search_assets(
            query=request.query,
            category=request.category,
            limit=request.limit
        )
        
        return {
            "assets": [
                {
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "category": asset.category.value,
                    "exchange": asset.exchange,
                    "description": asset.description
                }
                for asset in assets
            ],
            "count": len(assets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assets/{symbol}")
async def get_asset_details(symbol: str):
    """Get detailed information about a specific asset"""
    try:
        asset = asset_manager.get_asset_by_symbol(symbol)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Get current market data
        market_data = await data_fetcher.get_market_data(symbol)
        
        response = {
            "asset": {
                "symbol": asset.symbol,
                "name": asset.name,
                "category": asset.category.value,
                "exchange": asset.exchange,
                "description": asset.description
            }
        }
        
        if market_data:
            response["market_data"] = {
                "price": market_data.price,
                "change_24h": market_data.change_24h,
                "change_percent_24h": market_data.change_percent_24h,
                "volume_24h": market_data.volume_24h,
                "market_cap": market_data.market_cap,
                "high_24h": market_data.high_24h,
                "low_24h": market_data.low_24h,
                "last_updated": market_data.last_updated.isoformat() if market_data.last_updated else None
            }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Market data endpoints
@app.get("/market/{symbol}/ohlcv")
async def get_ohlcv_data(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100
):
    """Get OHLCV (candlestick) data for an asset"""
    try:
        ohlcv_data = await data_fetcher.get_ohlcv_data(symbol, timeframe, limit)
        
        if not ohlcv_data:
            raise HTTPException(status_code=404, detail="No data found for this asset")
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": [
                {
                    "timestamp": candle.timestamp.isoformat(),
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "volume": candle.volume
                }
                for candle in ohlcv_data
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/{symbol}/current")
async def get_current_price(symbol: str):
    """Get current market data for an asset"""
    try:
        market_data = await data_fetcher.get_market_data(symbol)
        
        if not market_data:
            raise HTTPException(status_code=404, detail="No data found for this asset")
        
        return {
            "symbol": symbol,
            "price": market_data.price,
            "change_24h": market_data.change_24h,
            "change_percent_24h": market_data.change_percent_24h,
            "volume_24h": market_data.volume_24h,
            "market_cap": market_data.market_cap,
            "high_24h": market_data.high_24h,
            "low_24h": market_data.low_24h,
            "last_updated": market_data.last_updated.isoformat() if market_data.last_updated else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ML prediction endpoints
@app.post("/predictions/generate")
async def generate_prediction(request: PredictionRequest):
    """Generate AI trading prediction for an asset"""
    try:
        # Get historical data
        ohlcv_data = await data_fetcher.get_ohlcv_data(
            request.symbol,
            request.timeframe,
            request.periods
        )
        
        if not ohlcv_data or len(ohlcv_data) < 50:
            raise HTTPException(
                status_code=400,
                detail="Insufficient data for prediction (minimum 50 data points required)"
            )
        
        # Convert to DataFrame
        from data_fetcher_enhanced import ohlcv_to_dataframe
        df = ohlcv_to_dataframe(ohlcv_data)
        df['symbol'] = request.symbol
        
        # Generate prediction
        signal = ml_predictor.predict(df)
        
        return {
            "symbol": request.symbol,
            "signal": signal.signal.value,
            "confidence": signal.confidence,
            "entry_price": signal.entry_price,
            "target_price": signal.target_price,
            "stop_loss": signal.stop_loss,
            "reasoning": signal.reasoning,
            "timestamp": signal.timestamp.isoformat(),
            "recommendation": _get_recommendation_text(signal)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prediction for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_recommendation_text(signal: TradingSignal) -> str:
    """Convert trading signal to human-readable recommendation"""
    
    confidence_level = "high" if signal.confidence > 75 else "medium" if signal.confidence > 50 else "low"
    
    if signal.signal == SignalType.BUY:
        return f"Consider buying with {confidence_level} confidence. Target: ${signal.target_price:.4f}, Stop Loss: ${signal.stop_loss:.4f}"
    elif signal.signal == SignalType.SELL:
        return f"Consider selling with {confidence_level} confidence. Target: ${signal.target_price:.4f}, Stop Loss: ${signal.stop_loss:.4f}"
    else:
        return f"Hold position with {confidence_level} confidence. Monitor for changes."

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                symbol = message.get("symbol")
                if symbol:
                    manager.subscribe(websocket, symbol)
                    await real_time_manager.add_symbol(symbol)
                    
                    # Send confirmation
                    await manager.send_personal_message({
                        "type": "subscription_confirmed",
                        "symbol": symbol
                    }, websocket)
            
            elif message.get("type") == "unsubscribe":
                symbol = message.get("symbol")
                if symbol:
                    # Remove from subscriptions (handled in disconnect)
                    await real_time_manager.remove_symbol(symbol)
                    
                    # Send confirmation
                    await manager.send_personal_message({
                        "type": "unsubscription_confirmed",
                        "symbol": symbol
                    }, websocket)
            
            elif message.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

# Training endpoint (for model updates)
@app.post("/models/train")
async def train_models(background_tasks: BackgroundTasks):
    """Train ML models with latest data (background task)"""
    
    async def train_task():
        try:
            logger.info("Starting model training...")
            
            # Get sample training data (you'd implement proper data collection)
            # For now, this is a placeholder
            sample_symbols = ["BTCUSDT", "ETHUSD", "EURUSD", "GOLD", "SPY"]
            
            for symbol in sample_symbols:
                try:
                    ohlcv_data = await data_fetcher.get_ohlcv_data(symbol, "1h", 1000)
                    if ohlcv_data and len(ohlcv_data) >= 100:
                        from data_fetcher_enhanced import ohlcv_to_dataframe
                        df = ohlcv_to_dataframe(ohlcv_data)
                        df['symbol'] = symbol
                        
                        # Train models
                        results = ml_predictor.train(df)
                        logger.info(f"Trained models for {symbol}: {results}")
                        
                        # Save models
                        ml_predictor.save_models("./models")
                        
                        break  # Train on first successful dataset for now
                        
                except Exception as e:
                    logger.error(f"Error training on {symbol}: {e}")
            
            logger.info("Model training completed")
            
        except Exception as e:
            logger.error(f"Error in training task: {e}")
    
    background_tasks.add_task(train_task)
    
    return {
        "message": "Model training started in background",
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
