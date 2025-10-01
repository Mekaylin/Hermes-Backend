"""
AI Trading Agent for Hermes Trading Companion

This module provides a comprehensive trading agent that uses GPT to analyze
market data, technical indicators, and news sentiment to generate trading signals.
"""

from __future__ import annotations
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np
from enum import Enum

# Trading libraries
import yfinance as yf
# import talib  # Optional - will use pandas for calculations if not available
import requests
from transformers import pipeline

# OpenAI for GPT
import openai

# Configuration
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Signal(Enum):
    """Trading signal enumeration."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class TradingPrediction:
    """Structured trading prediction from the AI agent."""
    symbol: str
    signal: Signal
    confidence: float  # 0-100
    reasoning: List[str]
    entry_price: Optional[float]
    stop_loss: Optional[float]
    target_price: Optional[float]
    timestamp: datetime
    timeframe: str
    risk_level: str = "MEDIUM"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "symbol": self.symbol,
            "signal": self.signal.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "target_price": self.target_price,
            "timestamp": self.timestamp.isoformat(),
            "timeframe": self.timeframe,
            "risk_level": self.risk_level
        }


class AgentGuardrail:
    """
    Lightweight safety/guardrail enforcement for trading predictions.

    This class enforces simple, auditable rules to prevent high-risk or
    malformed recommendations from being returned by the agent. Rules are
    intentionally conservative and can be extended later (compliance hooks,
    risk calculations, stateful exposure limits, rate limits, etc.).
    """

    def __init__(self, max_confidence: float = 95.0, max_position_risk_pct: float = 0.05, banned_symbols: Optional[List[str]] = None):
        self.max_confidence = float(max_confidence)
        self.max_position_risk_pct = float(max_position_risk_pct)
        self.banned_symbols = set([s.strip().upper() for s in (banned_symbols or []) if s.strip()])

    def enforce(self, prediction: "TradingPrediction", market_data: Optional['MarketData'] = None) -> Tuple['TradingPrediction', List[str]]:
        """Validate and (if needed) adjust a TradingPrediction.

        Returns the (possibly modified) prediction and a list of guard flags.
        """
        flags: List[str] = []

        # Ban trading certain symbols
        symbol = (market_data.symbol if market_data and getattr(market_data, 'symbol', None) else getattr(prediction, 'symbol', None))
        if symbol and symbol.upper() in self.banned_symbols:
            flags.append('banned_symbol')
            # Force conservative response
            prediction.signal = Signal.HOLD
            prediction.confidence = 0.0
            prediction.reasoning.insert(0, 'Guardrail: trading is banned for this symbol')
            return prediction, flags

        # Ensure trades include stop-loss/entry for BUY/SELL
        if prediction.signal in (Signal.BUY, Signal.SELL):
            if prediction.entry_price is None or prediction.stop_loss is None:
                flags.append('missing_entry_or_stop')
                prediction.signal = Signal.HOLD
                prediction.confidence = min(prediction.confidence, 50.0)
                prediction.reasoning.insert(0, 'Guardrail: missing entry or stop-loss -> switched to HOLD')

        # Simple risk-per-share check (relative to current price)
        try:
            if market_data and market_data.current_price and prediction.stop_loss and prediction.entry_price:
                current = float(market_data.current_price)
                if current > 0:
                    risk_per_share = abs(float(prediction.entry_price) - float(prediction.stop_loss))
                    # risk as fraction of price
                    risk_frac = risk_per_share / current
                    if risk_frac > 0.5:
                        flags.append('excessive_risk_fraction')
                        prediction.confidence = min(prediction.confidence, 40.0)
                        prediction.reasoning.insert(0, 'Guardrail: excessive per-share risk detected; confidence reduced')
        except Exception:
            # Non-fatal - don't block prediction for calculation errors
            pass

        # Cap confidence to a safe maximum
        if prediction.confidence is not None and prediction.confidence > self.max_confidence:
            flags.append('confidence_capped')
            prediction.confidence = float(self.max_confidence)
            prediction.reasoning.insert(0, f'Guardrail: confidence capped at {self.max_confidence}')

        return prediction, flags


@dataclass
class MarketData:
    """Market data container."""
    symbol: str
    current_price: float
    ohlcv: pd.DataFrame
    technical_indicators: Dict[str, float]
    volume_profile: Dict[str, float]
    volatility: float


@dataclass
class NewsData:
    """News sentiment data container."""
    headlines: List[str]
    sentiment_score: float  # -1 to 1
    sentiment_label: str
    news_count: int


class TechnicalAnalyzer:
    """Technical analysis utilities."""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate comprehensive technical indicators.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dict of technical indicators
        """
        try:
            close = df['Close'].values
            high = df['High'].values
            low = df['Low'].values
            volume = df['Volume'].values
            
            indicators = {}
            
            # Moving Averages using pandas
            indicators['EMA_12'] = df['Close'].ewm(span=12).mean().iloc[-1] if len(df) >= 12 else None
            indicators['EMA_26'] = df['Close'].ewm(span=26).mean().iloc[-1] if len(df) >= 26 else None
            indicators['SMA_50'] = df['Close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
            indicators['SMA_200'] = df['Close'].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else None
            
            # RSI calculation
            if len(df) >= 14:
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                indicators['RSI'] = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD calculation
            if len(df) >= 26:
                ema_12 = df['Close'].ewm(span=12).mean()
                ema_26 = df['Close'].ewm(span=26).mean()
                macd = ema_12 - ema_26
                macd_signal = macd.ewm(span=9).mean()
                macd_histogram = macd - macd_signal
                
                indicators['MACD'] = macd.iloc[-1]
                indicators['MACD_Signal'] = macd_signal.iloc[-1]
                indicators['MACD_Histogram'] = macd_histogram.iloc[-1]
            
            # Bollinger Bands
            if len(df) >= 20:
                sma_20 = df['Close'].rolling(window=20).mean()
                std_20 = df['Close'].rolling(window=20).std()
                indicators['BB_Upper'] = (sma_20 + (std_20 * 2)).iloc[-1]
                indicators['BB_Middle'] = sma_20.iloc[-1]
                indicators['BB_Lower'] = (sma_20 - (std_20 * 2)).iloc[-1]
            
            # Volume indicators
            indicators['Volume_SMA'] = df['Volume'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else None
            
            # Average True Range (ATR) calculation
            if len(df) >= 14:
                high_low = df['High'] - df['Low']
                high_close = np.abs(df['High'] - df['Close'].shift())
                low_close = np.abs(df['Low'] - df['Close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                indicators['ATR'] = true_range.rolling(window=14).mean().iloc[-1]
            
            # Support and Resistance levels
            indicators['Support'] = df['Low'].rolling(window=20).min().iloc[-1] if len(df) >= 20 else None
            indicators['Resistance'] = df['High'].rolling(window=20).max().iloc[-1] if len(df) >= 20 else None
            
            # Clean up NaN values
            indicators = {k: v for k, v in indicators.items() if v is not None and not np.isnan(v)}
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}


class MarketDataFetcher:
    """Fetches real-time and historical market data."""
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        
    async def fetch_historical_data(self, symbol: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTC-USD')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for symbol {symbol}")
                return pd.DataFrame()
                
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Missing required columns in data for {symbol}")
                return pd.DataFrame()
                
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_current_price(self, symbol: str) -> Optional[float]:
        """
        Fetch current market price for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Current price or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    async def fetch_market_data(self, symbol: str, timeframe: str = "1d") -> Optional[MarketData]:
        """
        Fetch comprehensive market data for analysis.
        
        Args:
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            MarketData object or None if failed
        """
        try:
            # Fetch historical data
            df = await self.fetch_historical_data(symbol, period="6mo", interval=timeframe)
            if df.empty:
                return None
                
            # Get current price
            current_price = await self.fetch_current_price(symbol)
            if current_price is None:
                current_price = df['Close'].iloc[-1]
            
            # Calculate technical indicators
            technical_indicators = TechnicalAnalyzer.calculate_indicators(df)
            
            # Calculate volatility
            returns = df['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            
            # Volume profile
            volume_profile = {
                'avg_volume': df['Volume'].mean(),
                'current_volume': df['Volume'].iloc[-1],
                'volume_ratio': df['Volume'].iloc[-1] / df['Volume'].mean() if df['Volume'].mean() > 0 else 1
            }
            
            return MarketData(
                symbol=symbol,
                current_price=current_price,
                ohlcv=df,
                technical_indicators=technical_indicators,
                volume_profile=volume_profile,
                volatility=volatility
            )
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None


class NewsAnalyzer:
    """Analyzes news sentiment for trading decisions."""
    
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.sentiment_analyzer = None
        
        # Try to initialize FinBERT sentiment analyzer
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert"
            )
            logger.info("FinBERT sentiment analyzer initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize FinBERT: {e}")
            # Fallback to basic sentiment analyzer
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis")
                logger.info("Basic sentiment analyzer initialized")
            except Exception as e2:
                logger.error(f"Failed to initialize any sentiment analyzer: {e2}")
    
    async def fetch_news(self, symbol: str, limit: int = 10) -> List[str]:
        """
        Fetch recent news headlines for a symbol.
        
        Args:
            symbol: Trading symbol
            limit: Number of headlines to fetch
            
        Returns:
            List of news headlines
        """
        headlines = []
        
        if not self.news_api_key:
            logger.warning("No NEWS_API_KEY found, using mock headlines")
            return [
                f"{symbol} shows strong momentum in today's trading session",
                f"Analysts upgrade {symbol} price target following strong earnings",
                f"Market volatility affects {symbol} trading volume"
            ]
        
        try:
            # Search for news about the symbol
            company_name = symbol.replace('-USD', '').replace('-', ' ')
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': f'{company_name} OR {symbol}',
                'sortBy': 'publishedAt',
                'pageSize': limit,
                'language': 'en',
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                headlines = [article['title'] for article in data.get('articles', [])]
            else:
                logger.warning(f"News API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            
        return headlines[:limit] if headlines else []
    
    def analyze_sentiment(self, headlines: List[str]) -> Tuple[float, str]:
        """
        Analyze sentiment of news headlines.
        
        Args:
            headlines: List of news headlines
            
        Returns:
            Tuple of (sentiment_score, sentiment_label)
        """
        if not headlines or not self.sentiment_analyzer:
            return 0.0, "NEUTRAL"
        
        try:
            sentiments = []
            for headline in headlines:
                result = self.sentiment_analyzer(headline[:512])  # Truncate for model limits
                if isinstance(result, list) and len(result) > 0:
                    sentiment = result[0]
                    label = sentiment['label'].upper()
                    score = sentiment['score']
                    
                    # Convert to numerical score (-1 to 1)
                    if 'POSITIVE' in label:
                        sentiments.append(score)
                    elif 'NEGATIVE' in label:
                        sentiments.append(-score)
                    else:
                        sentiments.append(0.0)
            
            if not sentiments:
                return 0.0, "NEUTRAL"
            
            avg_sentiment = np.mean(sentiments)
            
            # Determine overall label
            if avg_sentiment > 0.1:
                label = "POSITIVE"
            elif avg_sentiment < -0.1:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"
                
            return float(avg_sentiment), label
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0, "NEUTRAL"
    
    async def get_news_sentiment(self, symbol: str) -> NewsData:
        """
        Get comprehensive news sentiment analysis.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            NewsData object
        """
        headlines = await self.fetch_news(symbol)
        sentiment_score, sentiment_label = self.analyze_sentiment(headlines)
        
        return NewsData(
            headlines=headlines,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            news_count=len(headlines)
        )


class TradingAgent:
    """
    AI-powered trading agent that analyzes market data and generates trading signals.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.market_fetcher = MarketDataFetcher()
        self.news_analyzer = NewsAnalyzer()
        self.cache = {}  # Simple memory cache
        self.cache_ttl = 300  # 5 minutes cache TTL
        
        # Initialize OpenAI
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("No OPENAI_API_KEY found, predictions will use fallback logic")
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid."""
        if cache_key not in self.cache:
            return False
        return time.time() - self.cache[cache_key]['timestamp'] < self.cache_ttl
    
    def _get_cache_key(self, symbol: str, timeframe: str) -> str:
        """Generate cache key for symbol and timeframe."""
        return f"{symbol}_{timeframe}"
    
    def _generate_gpt_prompt(self, market_data: MarketData, news_data: NewsData) -> str:
        """
        Generate a comprehensive prompt for GPT analysis.
        
        Args:
            market_data: Market data and technical indicators
            news_data: News sentiment analysis
            
        Returns:
            Structured prompt for GPT
        """
        prompt = f"""
You are the world's best AI trading analyst with decades of experience in technical analysis, fundamental analysis, and market psychology. Analyze the following market data and provide a detailed trading recommendation.

MARKET DATA FOR {market_data.symbol}:
Current Price: ${market_data.current_price:.2f}
Volatility (Annualized): {market_data.volatility:.2%}

TECHNICAL INDICATORS:
"""
        
        # Add technical indicators
        for indicator, value in market_data.technical_indicators.items():
            if value is not None:
                prompt += f"- {indicator}: {value:.4f}\n"
        
        prompt += f"""
VOLUME ANALYSIS:
- Average Volume: {market_data.volume_profile['avg_volume']:,.0f}
- Current Volume: {market_data.volume_profile['current_volume']:,.0f}
- Volume Ratio: {market_data.volume_profile['volume_ratio']:.2f}x

NEWS SENTIMENT ANALYSIS:
- Overall Sentiment: {news_data.sentiment_label}
- Sentiment Score: {news_data.sentiment_score:.3f} (-1 to +1 scale)
- News Headlines Count: {news_data.news_count}
- Recent Headlines: {'; '.join(news_data.headlines[:3])}

TRADING ANALYSIS FRAMEWORK:
1. Technical Analysis: Analyze price action, support/resistance, trend direction, momentum indicators
2. Market Structure: Evaluate market phase (trending, ranging, breakout, reversal)
3. Risk Assessment: Consider volatility, volume patterns, and market conditions
4. News Impact: Factor in sentiment and potential market-moving events
5. Risk Management: Set appropriate stop-loss and take-profit levels

REQUIRED RESPONSE FORMAT (JSON):
{{
    "signal": "BUY|SELL|HOLD",
    "confidence": <0-100>,
    "reasoning": [
        "Technical analysis findings",
        "Market structure assessment", 
        "Risk factors and considerations",
        "News sentiment impact"
    ],
    "entry_price": <recommended entry price>,
    "stop_loss": <stop loss price>,
    "target_price": <profit target price>,
    "risk_level": "LOW|MEDIUM|HIGH",
    "time_horizon": "SHORT|MEDIUM|LONG"
}}

IMPORTANT GUIDELINES:
- Be conservative with high-risk trades
- Always include stop-loss recommendations
- Consider current market volatility in position sizing
- Factor in news sentiment but don't let it override technical analysis
- Provide clear, actionable reasoning
- Be honest about uncertainty - use HOLD when signals are mixed

Provide your analysis and trading recommendation:"""

        return prompt
    
    def _parse_gpt_response(self, response_text: str, symbol: str, timeframe: str) -> TradingPrediction:
        """
        Parse GPT response into a structured prediction.
        
        Args:
            response_text: Raw GPT response
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            TradingPrediction object
        """
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                signal = Signal(data.get('signal', 'HOLD'))
                confidence = min(max(float(data.get('confidence', 50)), 0), 100)
                reasoning = data.get('reasoning', ['GPT analysis completed'])
                entry_price = data.get('entry_price')
                stop_loss = data.get('stop_loss')
                target_price = data.get('target_price')
                risk_level = data.get('risk_level', 'MEDIUM')
                
                return TradingPrediction(
                    symbol=symbol,
                    signal=signal,
                    confidence=confidence,
                    reasoning=reasoning,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    target_price=target_price,
                    timestamp=datetime.now(),
                    timeframe=timeframe,
                    risk_level=risk_level
                )
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing GPT response: {e}")
            # Fallback prediction
            return TradingPrediction(
                symbol=symbol,
                signal=Signal.HOLD,
                confidence=50.0,
                reasoning=[f"Unable to parse GPT response: {str(e)}"],
                entry_price=None,
                stop_loss=None,
                target_price=None,
                timestamp=datetime.now(),
                timeframe=timeframe,
                risk_level="HIGH"
            )
    
    async def _call_gpt(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Call GPT API with the analysis prompt.
        
        Args:
            prompt: Analysis prompt
            
        Returns:
            GPT response text
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            # Dynamically select model from parameter or config
            try:
                from .config import settings
            except Exception:
                # fallback to environment
                settings = None

            chosen_model = model or (getattr(settings, 'OPENAI_MODEL', None) if settings is not None else None) or os.getenv('OPENAI_MODEL', 'gpt-4')

            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model=chosen_model,
                messages=[
                    {"role": "system", "content": "You are a professional trading analyst with expertise in technical analysis and market psychology."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(getattr(settings, 'OPENAI_MAX_TOKENS', os.getenv('OPENAI_MAX_TOKENS', 1500))),
                temperature=float(getattr(settings, 'OPENAI_TEMPERATURE', os.getenv('OPENAI_TEMPERATURE', 0.3))),
                response_format={"type": "json_object"}
            )

            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling GPT API: {e}")
            raise
    
    def _generate_fallback_prediction(self, market_data: MarketData, news_data: NewsData, timeframe: str) -> TradingPrediction:
        """
        Generate a fallback prediction using simple technical analysis when GPT is unavailable.
        
        Args:
            market_data: Market data
            news_data: News sentiment
            timeframe: Analysis timeframe
            
        Returns:
            TradingPrediction based on technical indicators
        """
        indicators = market_data.technical_indicators
        current_price = market_data.current_price
        
        # Simple scoring system
        score = 0
        reasoning = []
        
        # RSI analysis
        rsi = indicators.get('RSI')
        if rsi:
            if rsi < 30:
                score += 2
                reasoning.append(f"RSI oversold at {rsi:.1f}")
            elif rsi > 70:
                score -= 2
                reasoning.append(f"RSI overbought at {rsi:.1f}")
            elif rsi < 50:
                score += 1
                reasoning.append(f"RSI below midline at {rsi:.1f}")
            else:
                score -= 1
                reasoning.append(f"RSI above midline at {rsi:.1f}")
        
        # Moving average analysis
        ema_12 = indicators.get('EMA_12')
        ema_26 = indicators.get('EMA_26')
        if ema_12 and ema_26:
            if ema_12 > ema_26:
                score += 1
                reasoning.append("Short-term EMA above long-term EMA (bullish)")
            else:
                score -= 1
                reasoning.append("Short-term EMA below long-term EMA (bearish)")
        
        # MACD analysis
        macd = indicators.get('MACD')
        macd_signal = indicators.get('MACD_Signal')
        if macd and macd_signal:
            if macd > macd_signal:
                score += 1
                reasoning.append("MACD above signal line (bullish)")
            else:
                score -= 1
                reasoning.append("MACD below signal line (bearish)")
        
        # News sentiment
        if news_data.sentiment_score > 0.2:
            score += 1
            reasoning.append(f"Positive news sentiment ({news_data.sentiment_score:.2f})")
        elif news_data.sentiment_score < -0.2:
            score -= 1
            reasoning.append(f"Negative news sentiment ({news_data.sentiment_score:.2f})")
        
        # Volume analysis
        volume_ratio = market_data.volume_profile['volume_ratio']
        if volume_ratio > 1.5:
            reasoning.append(f"High volume ({volume_ratio:.1f}x average)")
        elif volume_ratio < 0.5:
            reasoning.append(f"Low volume ({volume_ratio:.1f}x average)")
        
        # Determine signal
        if score >= 3:
            signal = Signal.BUY
            confidence = min(70 + score * 5, 95)
        elif score <= -3:
            signal = Signal.SELL
            confidence = min(70 + abs(score) * 5, 95)
        else:
            signal = Signal.HOLD
            confidence = 50
        
        # Calculate entry, stop loss, and target prices
        atr = indicators.get('ATR', current_price * 0.02)  # 2% fallback
        
        if signal == Signal.BUY:
            entry_price = current_price
            stop_loss = current_price - (atr * 2)
            target_price = current_price + (atr * 3)
        elif signal == Signal.SELL:
            entry_price = current_price
            stop_loss = current_price + (atr * 2)
            target_price = current_price - (atr * 3)
        else:
            entry_price = current_price
            stop_loss = None
            target_price = None
        
        reasoning.append("Analysis based on technical indicators (GPT unavailable)")
        
        return TradingPrediction(
            symbol=market_data.symbol,
            signal=signal,
            confidence=confidence,
            reasoning=reasoning,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            timestamp=datetime.now(),
            timeframe=timeframe,
            risk_level="MEDIUM"
        )
    
    async def analyze_asset(self, symbol: str, timeframe: str = "1d") -> TradingPrediction:
        """
        Perform comprehensive analysis of an asset and generate trading prediction.
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTC-USD')
            timeframe: Analysis timeframe ('1d', '1h', '15m', etc.)
            
        Returns:
            TradingPrediction with detailed analysis
        """
        cache_key = self._get_cache_key(symbol, timeframe)
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached prediction for {symbol}")
            return self.cache[cache_key]['prediction']
        
        try:
            logger.info(f"Starting analysis for {symbol} on {timeframe} timeframe")
            
            # Fetch market data and news in parallel
            market_data_task = self.market_fetcher.fetch_market_data(symbol, timeframe)
            news_data_task = self.news_analyzer.get_news_sentiment(symbol)
            
            market_data, news_data = await asyncio.gather(market_data_task, news_data_task)
            
            if not market_data:
                raise ValueError(f"Unable to fetch market data for {symbol}")
            
            prediction = None
            
            # Try GPT analysis first
            if self.openai_api_key:
                try:
                    prompt = self._generate_gpt_prompt(market_data, news_data)
                    
                    # Debug: log the prompt if debug mode is enabled
                    if os.getenv('DEBUG_PROMPTS', '').lower() == 'true':
                        logger.debug(f"GPT Prompt for {symbol}:\n{prompt}")
                    
                    gpt_response = await self._call_gpt(prompt)
                    prediction = self._parse_gpt_response(gpt_response, symbol, timeframe)
                    
                    logger.info(f"GPT analysis completed for {symbol}: {prediction.signal.value} with {prediction.confidence}% confidence")
                    
                except Exception as e:
                    logger.error(f"GPT analysis failed for {symbol}: {e}")
                    prediction = None
            
            # Fallback to technical analysis if GPT failed
            if not prediction:
                logger.info(f"Using fallback technical analysis for {symbol}")
                prediction = self._generate_fallback_prediction(market_data, news_data, timeframe)
            
            # Apply guardrails before caching/returning
            try:
                guard = AgentGuardrail()
                prediction, guard_flags = guard.enforce(prediction, market_data)
                if guard_flags:
                    # Annotate reasoning with guard flags for auditability
                    prediction.reasoning.append(f"guard_flags={guard_flags}")
            except Exception as e:
                logger.error(f"Guardrail enforcement failed: {e}")

            # Cache the (possibly modified) result
            self.cache[cache_key] = {
                'prediction': prediction,
                'timestamp': time.time()
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            
            # Return a safe fallback prediction
            return TradingPrediction(
                symbol=symbol,
                signal=Signal.HOLD,
                confidence=30.0,
                reasoning=[f"Analysis failed: {str(e)}"],
                entry_price=None,
                stop_loss=None,
                target_price=None,
                timestamp=datetime.now(),
                timeframe=timeframe,
                risk_level="HIGH"
            )
    
    def get_debug_info(self, symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
        """
        Get debug information for troubleshooting.
        
        Args:
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            Debug information dictionary
        """
        return {
            "agent_status": {
                "openai_configured": bool(self.openai_api_key),
                "news_api_configured": bool(self.news_analyzer.news_api_key),
                "sentiment_analyzer": bool(self.news_analyzer.sentiment_analyzer),
                "cache_entries": len(self.cache)
            },
            "symbol": symbol,
            "timeframe": timeframe,
            "cache_key": self._get_cache_key(symbol, timeframe),
            "cache_valid": self._is_cache_valid(self._get_cache_key(symbol, timeframe))
        }


# Export main classes
__all__ = ['TradingAgent', 'TradingPrediction', 'Signal', 'MarketData', 'NewsData']
