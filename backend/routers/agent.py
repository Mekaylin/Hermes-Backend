"""
FastAPI router for AI Trading Agent endpoints.

This module provides RESTful API endpoints for the AI trading agent,
including prediction generation, analysis, and debug utilities.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, File, UploadFile, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import time
from pydantic import Json
from datetime import datetime
import logging

# Prefer absolute package import when running as a package (backend.*)
try:
    from backend.agent import TradingAgent, TradingPrediction, Signal  # type: ignore
except Exception:
    try:
        # Fallback to top-level import for development where backend may be on PYTHONPATH
        from agent import TradingAgent, TradingPrediction, Signal  # type: ignore
    except Exception:
        TradingAgent = None  # type: ignore
        TradingPrediction = None  # type: ignore
        Signal = None  # type: ignore

from .. import ai_training


# If the actual TradingAgent couldn't be imported at module import time,
# provide a small proxy that raises a clear runtime error when used. This
# prevents FastAPI from failing to include the router while giving a
# descriptive error if an endpoint that requires the agent is called.
class _AgentUnavailable:
    def __getattr__(self, item):
        raise RuntimeError(
            "TradingAgent is not importable. Check backend/agent.py and ensure it exports `TradingAgent`."
        )

# Instantiate trading_agent if available, otherwise use proxy
trading_agent = TradingAgent() if TradingAgent is not None else _AgentUnavailable()

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/agent", tags=["AI Trading Agent"])


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    """Request model for trading predictions."""
    symbol: str = Field(..., description="Trading symbol (e.g., 'AAPL', 'BTC-USD')")
    timeframe: str = Field(default="1d", description="Analysis timeframe ('1d', '1h', '15m', etc.)")
    force_refresh: bool = Field(default=False, description="Force refresh, ignore cache")


class PredictionResponse(BaseModel):
    """Response model for trading predictions."""
    symbol: str
    signal: str
    confidence: float
    reasoning: List[str]
    entry_price: Optional[float]
    stop_loss: Optional[float]
    target_price: Optional[float]
    timestamp: datetime
    timeframe: str
    risk_level: str
    analysis_time_ms: Optional[int] = None
    cached: bool = False


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions."""
    symbols: List[str] = Field(..., description="List of trading symbols")
    timeframe: str = Field(default="1d", description="Analysis timeframe")
    max_concurrent: int = Field(default=5, description="Maximum concurrent analyses")


class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions."""
    predictions: List[PredictionResponse]
    total_symbols: int
    successful_analyses: int
    failed_analyses: int
    analysis_time_ms: int


class BacktestRequest(BaseModel):
    symbol: str = Field(..., description="Ticker symbol, e.g. 'AAPL'")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")


class BacktestResponse(BaseModel):
    backtest_id: int
    metrics: Dict[str, Any]
    equity_curve: List[Dict[str, Any]]
    csv_path: Optional[str]


class DebugResponse(BaseModel):
    """Response model for debug information."""
    agent_status: Dict[str, Any]
    symbol: str
    timeframe: str
    cache_key: str
    cache_valid: bool
    timestamp: datetime


@router.get("/health", summary="Agent Health Check")
async def agent_health():
    """
    Check the health status of the AI trading agent.
    
    Returns basic information about the agent's configuration and status.
    """
    try:
        debug_info = trading_agent.get_debug_info("AAPL")  # Use AAPL as test symbol
        
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


@router.post("/predict", response_model=PredictionResponse, summary="Generate Trading Prediction")
async def predict_trade(request: PredictionRequest):
    """
    Generate an AI-powered trading prediction for a specific symbol.
    
    This endpoint uses the full AI trading agent pipeline including:
    - Market data analysis with technical indicators
    - News sentiment analysis
    - GPT-powered decision making
    - Risk assessment and position sizing
    
    Args:
        request: Prediction request with symbol and parameters
        
    Returns:
        Comprehensive trading prediction with signal, confidence, and reasoning
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Generating prediction for {request.symbol} on {request.timeframe}")
        
        # Clear cache if force refresh is requested
        if request.force_refresh:
            cache_key = trading_agent._get_cache_key(request.symbol, request.timeframe)
            if cache_key in trading_agent.cache:
                del trading_agent.cache[cache_key]
                logger.info(f"Cache cleared for {request.symbol}")
        
        # Check if we have a cached result
        cache_key = trading_agent._get_cache_key(request.symbol, request.timeframe)
        cached = trading_agent._is_cache_valid(cache_key)
        
        # Generate prediction
        prediction = await trading_agent.analyze_asset(request.symbol, request.timeframe)
        
        # Calculate analysis time
        analysis_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = PredictionResponse(
            symbol=prediction.symbol,
            signal=prediction.signal.value,
            confidence=prediction.confidence,
            reasoning=prediction.reasoning,
            entry_price=prediction.entry_price,
            stop_loss=prediction.stop_loss,
            target_price=prediction.target_price,
            timestamp=prediction.timestamp,
            timeframe=prediction.timeframe,
            risk_level=prediction.risk_level,
            analysis_time_ms=int(analysis_time),
            cached=cached
        )
        
        logger.info(f"Prediction generated for {request.symbol}: {prediction.signal.value} "
                   f"({prediction.confidence}% confidence) in {analysis_time:.0f}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating prediction for {request.symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate prediction for {request.symbol}: {str(e)}"
        )


@router.post("/batch-predict", response_model=BatchPredictionResponse, summary="Batch Trading Predictions")
async def batch_predict(request: BatchPredictionRequest):
    """
    Generate trading predictions for multiple symbols in parallel.
    
    This endpoint allows efficient analysis of multiple assets simultaneously
    with configurable concurrency limits to manage API rate limits.
    
    Args:
        request: Batch prediction request with symbols list
        
    Returns:
        Batch prediction response with all results and summary statistics
    """
    start_time = datetime.now()
    
    try:
        import asyncio
        
        logger.info(f"Starting batch prediction for {len(request.symbols)} symbols")
        
        # Limit concurrent analyses to prevent API rate limiting
        semaphore = asyncio.Semaphore(min(request.max_concurrent, 10))
        
        async def analyze_with_semaphore(symbol: str):
            async with semaphore:
                try:
                    prediction = await trading_agent.analyze_asset(symbol, request.timeframe)
                    cache_key = trading_agent._get_cache_key(symbol, request.timeframe)
                    cached = trading_agent._is_cache_valid(cache_key)
                    
                    return PredictionResponse(
                        symbol=prediction.symbol,
                        signal=prediction.signal.value,
                        confidence=prediction.confidence,
                        reasoning=prediction.reasoning,
                        entry_price=prediction.entry_price,
                        stop_loss=prediction.stop_loss,
                        target_price=prediction.target_price,
                        timestamp=prediction.timestamp,
                        timeframe=prediction.timeframe,
                        risk_level=prediction.risk_level,
                        cached=cached
                    )
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
                    return None
        
        # Execute all analyses
        tasks = [analyze_with_semaphore(symbol) for symbol in request.symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful predictions
        predictions = [result for result in results if isinstance(result, PredictionResponse)]
        
        # Calculate statistics
        analysis_time = (datetime.now() - start_time).total_seconds() * 1000
        successful_analyses = len(predictions)
        failed_analyses = len(request.symbols) - successful_analyses
        
        logger.info(f"Batch prediction completed: {successful_analyses}/{len(request.symbols)} "
                   f"successful in {analysis_time:.0f}ms")
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_symbols=len(request.symbols),
            successful_analyses=successful_analyses,
            failed_analyses=failed_analyses,
            analysis_time_ms=int(analysis_time)
        )
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )



@router.post("/backtest", response_model=BacktestResponse, summary="Run Backtest")
async def run_backtest_endpoint(request: BacktestRequest, background_tasks: BackgroundTasks):
    """
    Run a backtest using the AI trading agent.

    This endpoint runs the synchronous `run_backtest` function in a threadpool
    to avoid blocking the event loop. It returns the backtest id, metrics and
    equity curve. The CSV path is returned for subsequent download.
    """
    try:
        # Lazy import to avoid circular imports at module import time
        from ..backtesting.engine import run_backtest
        import asyncio
        import concurrent.futures

        loop = asyncio.get_event_loop()

        # Run heavy CPU/IO work in threadpool
        def _run():
            return run_backtest(request.symbol, request.start_date, request.end_date)

        result = await loop.run_in_executor(None, _run)

        return BacktestResponse(
            backtest_id=result.get('backtest_id'),
            metrics=result.get('metrics'),
            equity_curve=result.get('equity_curve'),
            csv_path=result.get('csv_path')
        )

    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")



@router.post("/train", summary="Train the AI agent (dev)")
async def train_agent_endpoint(
    epochs: int = Form(3),
    symbol: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Trigger a training run using historical data.

    Accepts either an uploaded CSV file (as `file`) or a combination of
    `symbol`, `start_date`, and `end_date` to fetch data via yfinance.
    """
    try:
        import asyncio
        import tempfile
        loop = asyncio.get_event_loop()

        csv_path = None
        if file is not None:
            # Save uploaded file to a temp location
            suffix = os.path.splitext(file.filename)[1] if file.filename else '.csv'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                contents = file.file.read()
                tmp.write(contents)
                csv_path = tmp.name

        def _run():
            return ai_training.train_agent(epochs=epochs, symbol=symbol, start_date=start_date, end_date=end_date, csv_path=csv_path)

        result = await loop.run_in_executor(None, _run)

        # If we created a temp file, don't delete it immediately in case user wants to inspect; record path instead
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/test", summary="Run a quick test/eval of the agent (dev)")
async def test_agent_endpoint():
    try:
        import asyncio
        loop = asyncio.get_event_loop()

        def _run():
            return ai_training.test_agent()

        result = await loop.run_in_executor(None, _run)
        return {"status": "ok", "result": result}
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.get("/backtest/{backtest_id}/export", summary="Export Backtest Trades CSV")
async def export_backtest_csv(backtest_id: int):
    """
    Serve the CSV file for a completed backtest by id.

    Returns a FileResponse pointing to the CSV generated by the backtesting engine.
    """
    try:
        # CSVs are stored next to the DB in ../db/backtest_{id}_trades.csv
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'db')
        csv_path = os.path.join(base_dir, f'backtest_{backtest_id}_trades.csv')
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail=f"CSV for backtest {backtest_id} not found")

        return FileResponse(path=csv_path, filename=os.path.basename(csv_path), media_type='text/csv')

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting CSV for backtest {backtest_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")


@router.get("/predict/{symbol}", response_model=PredictionResponse, summary="Quick Prediction by Symbol")
async def quick_predict(
    symbol: str,
    timeframe: str = Query(default="1d", description="Analysis timeframe"),
    force_refresh: bool = Query(default=False, description="Force refresh, ignore cache")
):
    """
    Quick prediction endpoint for a specific symbol using URL path.
    
    This is a convenience endpoint that provides the same functionality
    as the POST /predict endpoint but with a simpler URL structure.
    
    Args:
        symbol: Trading symbol (e.g., 'AAPL', 'BTC-USD')
        timeframe: Analysis timeframe
        force_refresh: Force refresh, ignore cache
        
    Returns:
        Trading prediction response
    """
    request = PredictionRequest(
        symbol=symbol,
        timeframe=timeframe,
        force_refresh=force_refresh
    )
    return await predict_trade(request)


@router.get("/debug/{symbol}", response_model=DebugResponse, summary="Debug Information")
async def get_debug_info(
    symbol: str,
    timeframe: str = Query(default="1d", description="Analysis timeframe")
):
    """
    Get debug information for troubleshooting the AI trading agent.
    
    This endpoint provides detailed information about the agent's configuration,
    cache status, and other diagnostic data useful for debugging.
    
    Args:
        symbol: Trading symbol to check
        timeframe: Analysis timeframe
        
    Returns:
        Debug information including agent status and cache details
    """
    try:
        debug_info = trading_agent.get_debug_info(symbol, timeframe)
        
        return DebugResponse(
            agent_status=debug_info["agent_status"],
            symbol=debug_info["symbol"],
            timeframe=debug_info["timeframe"],
            cache_key=debug_info["cache_key"],
            cache_valid=debug_info["cache_valid"],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting debug info for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get debug info: {str(e)}"
        )


@router.delete("/cache", summary="Clear Prediction Cache")
async def clear_cache():
    """
    Clear the prediction cache to force fresh analysis.
    
    This endpoint clears all cached predictions, which can be useful
    during development or when you want to ensure fresh analysis results.
    
    Returns:
        Cache clearing confirmation with statistics
    """
    try:
        cache_entries = len(trading_agent.cache)
        trading_agent.cache.clear()
        
        logger.info(f"Cache cleared: {cache_entries} entries removed")
        
        return {
            "status": "success",
            "message": f"Cache cleared successfully",
            "entries_removed": cache_entries,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/cache/stats", summary="Cache Statistics")
async def get_cache_stats():
    """
    Get statistics about the prediction cache.
    
    Returns information about cache usage, hit rates, and performance metrics.
    
    Returns:
        Cache statistics and performance data
    """
    try:
        cache_entries = len(trading_agent.cache)
        
        # Get cache entry details
        cache_details = []
        for key, value in trading_agent.cache.items():
            cache_details.append({
                "key": key,
                "timestamp": datetime.fromtimestamp(value['timestamp']),
                "age_seconds": int(time.time() - value['timestamp']),
                "symbol": value['prediction'].symbol,
                "signal": value['prediction'].signal.value,
                "confidence": value['prediction'].confidence
            })
        
        return {
            "total_entries": cache_entries,
            "cache_ttl_seconds": trading_agent.cache_ttl,
            "entries": cache_details[:10],  # Show only first 10 entries
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache stats: {str(e)}"
        )


# Background task for warming up cache with popular symbols
async def warm_cache(symbols: List[str] = None):
    """
    Background task to warm up the cache with predictions for popular symbols.
    
    Args:
        symbols: List of symbols to warm up, defaults to popular stocks
    """
    if symbols is None:
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'BTC-USD', 'ETH-USD']
    
    try:
        logger.info(f"Starting cache warm-up for {len(symbols)} symbols")
        
        # Analyze each symbol
        for symbol in symbols:
            try:
                await trading_agent.analyze_asset(symbol)
                logger.info(f"Cache warmed for {symbol}")
            except Exception as e:
                logger.error(f"Failed to warm cache for {symbol}: {e}")
        
        logger.info("Cache warm-up completed")
        
    except Exception as e:
        logger.error(f"Cache warm-up failed: {e}")


@router.post("/cache/warm", summary="Warm Cache")
async def warm_cache_endpoint(
    background_tasks: BackgroundTasks,
    symbols: Optional[List[str]] = None
):
    """
    Start a background task to warm up the prediction cache.
    
    This endpoint initiates cache warming for popular trading symbols
    to improve response times for subsequent requests.
    
    Args:
        symbols: Optional list of symbols to warm up
        
    Returns:
        Cache warming confirmation
    """
    try:
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'BTC-USD', 'ETH-USD']
        
        background_tasks.add_task(warm_cache, symbols)
        
        return {
            "status": "success",
            "message": f"Cache warming started for {len(symbols)} symbols",
            "symbols": symbols,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error starting cache warm-up: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start cache warm-up: {str(e)}"
        )
