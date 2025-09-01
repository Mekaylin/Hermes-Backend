from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime
from market_scout import MarketScout
from database import store_prediction, get_predictions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hermes AI Market Analysis", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize market scout
scout = MarketScout()

class RecommendationResponse(BaseModel):
    symbol: str
    recommendation: str
    expected_return: float
    confidence: float
    risk_level: str
    current_price: float
    explanation: str
    timestamp: str

class TopRecommendationResponse(BaseModel):
    top_recommendation: RecommendationResponse
    confidence_pct: int
    expected_return_pct: str
    risk_level: str
    reasons: List[str]
    target_price: float
    stop_loss: float
    position_size_pct: float

@app.get("/")
def read_root():
    return {"message": "Hermes AI Market Analysis API", "status": "running"}

@app.get("/scout", response_model=List[RecommendationResponse])
def scout_assets(risk_preference: str = "Conservative", limit: int = 5):
    """Get top asset recommendations based on AI analysis"""
    try:
        logger.info(f"Scout request: risk={risk_preference}, limit={limit}")
        
        recommendations = scout.scout_all_assets(risk_preference)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No recommendations available")
        
        # Limit results
        limited_recommendations = recommendations[:limit]
        
        # Store predictions in database (if configured)
        try:
            for rec in limited_recommendations:
                store_prediction(
                    timestamp=datetime.datetime.now(),
                    asset=rec['symbol'],
                    signal=rec['recommendation'],
                    confidence=rec['confidence'],
                    predicted_change=rec['expected_return'],
                    model_version="scout_v1"
                )
        except Exception as e:
            logger.warning(f"Failed to store predictions: {e}")
        
        return [RecommendationResponse(**rec) for rec in limited_recommendations]
        
    except Exception as e:
        logger.error(f"Error in scout endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top-recommendation", response_model=TopRecommendationResponse)
def get_top_recommendation(risk_preference: str = "Conservative"):
    """Get the single best recommendation for novice users"""
    try:
        recommendations = scout.scout_all_assets(risk_preference)
        
        if not recommendations:
            raise HTTPException(status_code=404, detail="No recommendations available")
        
        top_rec = recommendations[0]
        
        # Calculate position sizing based on risk preference
        base_size = {"Conservative": 1.0, "Balanced": 2.0, "Aggressive": 4.0}
        position_size = min(base_size.get(risk_preference, 1.0) * top_rec['confidence'], 5.0)
        
        # Calculate target and stop loss
        current_price = top_rec['current_price']
        expected_return = top_rec['expected_return']
        volatility = top_rec['volatility']
        
        target_price = current_price * (1 + min(expected_return, 0.10))  # Cap at 10%
        stop_loss = current_price * (1 - 1.5 * volatility)  # 1.5x ATR stop
        
        # Format reasons
        reasons = [
            reason.strip() for reason in top_rec['explanation'].split(';')
            if reason.strip()
        ][:2]  # Limit to 2 reasons
        
        return TopRecommendationResponse(
            top_recommendation=RecommendationResponse(**top_rec),
            confidence_pct=int(top_rec['confidence'] * 100),
            expected_return_pct=f"{expected_return * 100:.1f}%",
            risk_level=top_rec['risk_level'],
            reasons=reasons,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size_pct=position_size
        )
        
    except Exception as e:
        logger.error(f"Error in top-recommendation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signal")
def get_signal(asset: str = "BTC-USD"):
    """Legacy endpoint for compatibility"""
    try:
        result = scout.scout_asset(asset)
        if not result:
            return {"signal": "hold", "confidence": 0.5, "predicted_change": 0.0}
        
        signal_map = {
            "Strong Buy": "buy",
            "Buy": "buy", 
            "Strong Sell": "sell",
            "Sell": "sell",
            "Hold": "hold"
        }
        
        return {
            "signal": signal_map.get(result['recommendation'], "hold"),
            "confidence": result['confidence'],
            "predicted_change": result['expected_return']
        }
        
    except Exception as e:
        logger.error(f"Error in signal endpoint: {e}")
        return {"signal": "hold", "confidence": 0.5, "predicted_change": 0.0}

@app.get("/history")
def get_history(asset: str = "BTC-USD"):
    """Get historical predictions and results"""
    try:
        history = get_predictions(asset)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error in history endpoint: {e}")
        return {"history": []}

@app.get("/news")
def get_news(asset: str = "BTC-USD"):
    """Get news with sentiment analysis"""
    try:
        sentiment = scout.fetch_news_sentiment(asset)
        
        # Mock news for now (replace with actual news fetching)
        news = [
            {
                "title": f"Market analysis for {asset}",
                "source": {"name": "Market AI"},
                "sentiment": 2 if sentiment > 0.3 else (0 if sentiment < -0.3 else 1),
                "sentiment_score": sentiment,
                "publishedAt": datetime.datetime.now().isoformat()
            }
        ]
        
        return {"news": news}
        
    except Exception as e:
        logger.error(f"Error in news endpoint: {e}")
        return {"news": []}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0"
    }
