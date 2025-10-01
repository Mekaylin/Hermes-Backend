"""
Standalone FastAPI application to test AI Trading Agent functionality.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import logging
from typing import Dict, Any

# Import our AI agent
from agent import TradingAgent, TradingPrediction, Signal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Hermes AI Trading Agent",
    description="AI-powered trading predictions using GPT and technical analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the trading agent
trading_agent = TradingAgent()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Hermes AI Trading Agent API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "agent_health": "/agent/health",
            "predict": "/agent/predict/{symbol}",
            "debug": "/agent/debug/{symbol}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "hermes-ai-trading-agent"
    }

@app.get("/agent/health")
async def agent_health():
    """Check the health status of the AI trading agent."""
    try:
        debug_info = trading_agent.get_debug_info("AAPL")
        
        return {
            "status": "healthy",
            "agent_configured": debug_info["agent_status"]["openai_configured"],
            "news_api_configured": debug_info["agent_status"]["news_api_configured"],
            "sentiment_analyzer": debug_info["agent_status"]["sentiment_analyzer"],
            "cache_entries": debug_info["agent_status"]["cache_entries"],
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Agent health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent health check failed: {str(e)}")

@app.get("/agent/predict/{symbol}")
async def predict_trade(symbol: str):
    """
    Generate an AI-powered trading prediction for a specific symbol.
    
    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTC-USD')
        
    Returns:
        Trading prediction with signal, confidence, and reasoning
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Generating prediction for {symbol}")
        
        # Generate prediction
        prediction = await trading_agent.analyze_asset(symbol, "1d")
        
        # Calculate analysis time
        analysis_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = {
            "symbol": prediction.symbol,
            "signal": prediction.signal.value,
            "confidence": prediction.confidence,
            "reasoning": prediction.reasoning,
            "entry_price": prediction.entry_price,
            "stop_loss": prediction.stop_loss,
            "target_price": prediction.target_price,
            "timestamp": prediction.timestamp.isoformat(),
            "timeframe": prediction.timeframe,
            "risk_level": prediction.risk_level,
            "analysis_time_ms": int(analysis_time)
        }
        
        logger.info(f"Prediction generated for {symbol}: {prediction.signal.value} "
                   f"({prediction.confidence}% confidence) in {analysis_time:.0f}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating prediction for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate prediction for {symbol}: {str(e)}"
        )

@app.get("/agent/debug/{symbol}")
async def get_debug_info(symbol: str):
    """Get debug information for troubleshooting the AI trading agent."""
    try:
        debug_info = trading_agent.get_debug_info(symbol, "1d")
        
        return {
            "agent_status": debug_info["agent_status"],
            "symbol": debug_info["symbol"],
            "timeframe": debug_info["timeframe"],
            "cache_key": debug_info["cache_key"],
            "cache_valid": debug_info["cache_valid"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting debug info for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get debug info: {str(e)}"
        )

@app.delete("/agent/cache")
async def clear_cache():
    """Clear the prediction cache to force fresh analysis."""
    try:
        cache_entries = len(trading_agent.cache)
        trading_agent.cache.clear()
        
        logger.info(f"Cache cleared: {cache_entries} entries removed")
        
        return {
            "status": "success",
            "message": f"Cache cleared successfully",
            "entries_removed": cache_entries,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )

if __name__ == "__main__":
    print("🚀 Starting Hermes AI Trading Agent API...")
    print("📊 Using fallback technical analysis (no GPT key configured)")
    print("🌐 Server will be available at http://localhost:8001")
    print("📖 API docs at http://localhost:8001/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=8001)
