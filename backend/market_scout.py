import yfinance as yf
import pandas as pd
import numpy as np
from ta import add_all_ta_features
import requests
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple
from config import ALPHA_VANTAGE_API_KEY, NEWS_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketScout:
    """Core scouting engine for asset recommendations"""
    
    def __init__(self):
        self.weights = {
            'w1': 0.5,  # GRU signal weight
            'w2': 0.3,  # predicted_pct_change weight
            'w3': 0.2,  # sentiment weight
            'w4': 0.2   # volatility penalty
        }
        
        # Default assets to track
        self.crypto_assets = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD', 'MATIC-USD']
        self.stock_assets = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'GOOGL']
        
    def fetch_price_data(self, symbol: str, period: str = "5d", interval: str = "1m") -> pd.DataFrame:
        """Fetch OHLCV data using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        if df.empty or len(df) < 50:
            return df
            
        try:
            # Add technical indicators
            df = add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume")
            
            # Calculate additional indicators
            df['ema_8'] = df['Close'].ewm(span=8).mean()
            df['ema_20'] = df['Close'].ewm(span=20).mean()
            df['ema_50'] = df['Close'].ewm(span=50).mean()
            
            # RSI
            df['rsi'] = df['momentum_rsi']
            
            # MACD
            df['macd'] = df['trend_macd']
            df['macd_signal'] = df['trend_macd_signal']
            df['macd_histogram'] = df['trend_macd_diff']
            
            # ATR for volatility
            df['atr'] = df['volatility_atr']
            
            # Price position relative to EMAs
            df['price_above_ema20'] = (df['Close'] > df['ema_20']).astype(int)
            df['price_above_ema50'] = (df['Close'] > df['ema_50']).astype(int)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df
    
    def simple_gru_prediction(self, df: pd.DataFrame) -> Dict:
        """Simplified GRU-like prediction using technical signals"""
        if df.empty or len(df) < 20:
            return {'p_up': 0.5, 'p_down': 0.5, 'pred_pct_change': 0.0, 'confidence': 0.0}
        
        try:
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Technical signals
            signals = []
            
            # EMA trend signal
            if latest['Close'] > latest['ema_20'] and latest['ema_20'] > latest['ema_50']:
                signals.append(0.8)  # Strong bullish
            elif latest['Close'] > latest['ema_20']:
                signals.append(0.6)  # Bullish
            elif latest['Close'] < latest['ema_20'] and latest['ema_20'] < latest['ema_50']:
                signals.append(0.2)  # Bearish
            else:
                signals.append(0.4)  # Neutral
            
            # RSI signal
            rsi = latest.get('rsi', 50)
            if 30 <= rsi <= 70:
                signals.append(0.7)  # Good range
            elif rsi < 30:
                signals.append(0.8)  # Oversold - potential buy
            elif rsi > 70:
                signals.append(0.3)  # Overbought - potential sell
            else:
                signals.append(0.5)
            
            # MACD signal
            macd = latest.get('macd', 0)
            macd_signal = latest.get('macd_signal', 0)
            if macd > macd_signal:
                signals.append(0.7)  # Bullish crossover
            else:
                signals.append(0.3)  # Bearish
            
            # Volume signal (simplified)
            volume_ma = df['Volume'].rolling(20).mean().iloc[-1]
            if latest['Volume'] > volume_ma * 1.2:
                signals.append(0.7)  # High volume
            else:
                signals.append(0.5)
            
            # Aggregate signals
            avg_signal = np.mean(signals)
            p_up = min(max(avg_signal, 0.1), 0.9)
            p_down = 1 - p_up
            
            # Predicted percentage change (simplified)
            price_change = (latest['Close'] - prev['Close']) / prev['Close']
            momentum = df['Close'].pct_change().rolling(5).mean().iloc[-1]
            pred_pct_change = momentum * 2  # Amplify for prediction
            
            # Confidence based on signal agreement
            signal_std = np.std(signals)
            confidence = max(0.1, 1 - signal_std)
            
            return {
                'p_up': p_up,
                'p_down': p_down,
                'pred_pct_change': pred_pct_change,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error in GRU prediction: {e}")
            return {'p_up': 0.5, 'p_down': 0.5, 'pred_pct_change': 0.0, 'confidence': 0.0}
    
    def fetch_news_sentiment(self, symbol: str) -> float:
        """Fetch and analyze news sentiment"""
        # Try to use FinBERT if available (optional heavy dependency)
        finbert = None
        try:
            from model_finbert import FinBERTSentiment
            finbert = FinBERTSentiment()
        except Exception:
            finbert = None

        try:
            # Extract base symbol for news search
            search_term = symbol.replace('-USD', '').replace('-USDT', '')
            if search_term in ['BTC', 'ETH', 'ADA', 'SOL', 'MATIC']:
                search_term = search_term + ' cryptocurrency'
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': search_term,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 10,
                'apiKey': NEWS_API_KEY
            }
            
            # If FinBERT loaded successfully, use it to analyse headlines first
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"News API error: {response.status_code}")
                return 0.0

            news_data = response.json()
            articles = news_data.get('articles', [])

            if not articles:
                return 0.0

            # If FinBERT is available, map its 3-class output to [-1,1]
            if finbert is not None:
                scores = []
                for article in articles[:5]:
                    text = f"{article.get('title','')} {article.get('description','')}"
                    try:
                        label, probs = finbert.predict_sentiment(text)
                        # label: 0 neg, 1 neutral, 2 pos -> map to -1..1
                        mapped = -1.0 if label == 0 else (0.0 if label == 1 else 1.0)
                        # weight by confidence (max prob)
                        confidence = max(probs) if isinstance(probs, (list, tuple)) else 1.0
                        scores.append(mapped * confidence)
                    except Exception:
                        # fallback to neutral for this article
                        scores.append(0.0)

                return float(np.mean(scores)) if scores else 0.0

            # Otherwise fallback to keyword heuristic
            positive_words = ['surge', 'rally', 'bullish', 'gains', 'up', 'rise', 'positive', 'strong', 'growth']
            negative_words = ['crash', 'fall', 'bearish', 'down', 'drop', 'negative', 'decline', 'weak', 'loss']

            sentiment_scores = []
            for article in articles[:5]:  # Analyze top 5 articles
                title = article.get('title', '').lower()
                description = article.get('description', '') or ''
                description = description.lower()
                text = f"{title} {description}"

                pos_count = sum(1 for word in positive_words if word in text)
                neg_count = sum(1 for word in negative_words if word in text)

                if pos_count > neg_count:
                    sentiment_scores.append(0.7)
                elif neg_count > pos_count:
                    sentiment_scores.append(-0.7)
                else:
                    sentiment_scores.append(0.0)

            return np.mean(sentiment_scores) if sentiment_scores else 0.0
            
        except Exception as e:
            logger.error(f"Error fetching sentiment for {symbol}: {e}")
            return 0.0
    
    def calculate_raw_score(self, symbol: str, gru_result: Dict, sentiment: float, volatility: float) -> float:
        """Calculate raw score using ensemble weights"""
        try:
            # Normalize inputs
            gru_signal = gru_result['p_up'] - gru_result['p_down']  # Range: -0.8 to 0.8
            pred_pct_normalized = np.tanh(gru_result['pred_pct_change'] * 100)  # Normalize to [-1, 1]
            volatility_normalized = min(volatility / 0.05, 1.0)  # Cap at 5% daily volatility
            
            # Calculate raw score
            raw_score = (
                self.weights['w1'] * gru_signal +
                self.weights['w2'] * pred_pct_normalized +
                self.weights['w3'] * sentiment -
                self.weights['w4'] * volatility_normalized
            )
            
            return raw_score
            
        except Exception as e:
            logger.error(f"Error calculating raw score for {symbol}: {e}")
            return 0.0
    
    def convert_to_expected_return(self, raw_score: float, volatility: float) -> Tuple[float, float]:
        """Convert raw score to expected return and confidence"""
        try:
            # Map raw score to expected return (calibrate based on historical data)
            # For now, use simple linear mapping
            expected_return = raw_score * 0.05  # Max 5% expected return
            
            # Apply risk adjustment
            risk_penalty = min(volatility / 0.03, 1.0)  # Penalty for high volatility
            risk_adjusted_return = expected_return * (1 - 0.5 * risk_penalty)
            
            # Calculate confidence based on score magnitude and volatility
            confidence = min(abs(raw_score) * 2, 0.9)  # Higher score = higher confidence
            confidence = confidence * (1 - risk_penalty * 0.3)  # Reduce confidence for volatile assets
            
            return risk_adjusted_return, confidence
            
        except Exception as e:
            logger.error(f"Error converting score to return: {e}")
            return 0.0, 0.0
    
    def scout_asset(self, symbol: str) -> Dict:
        """Scout a single asset and return recommendation"""
        try:
            logger.info(f"Scouting {symbol}")
            
            # Fetch price data
            df = self.fetch_price_data(symbol, period="5d", interval="15m")
            if df.empty:
                return None
            
            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)
            
            # Get GRU prediction
            gru_result = self.simple_gru_prediction(df)
            
            # Get sentiment
            sentiment = self.fetch_news_sentiment(symbol)
            
            # Calculate volatility (ATR as % of price)
            latest_price = df['Close'].iloc[-1]
            atr = df.get('atr', df['Close'].std()).iloc[-1] if 'atr' in df.columns else df['Close'].std()
            volatility = atr / latest_price if latest_price > 0 else 0.05
            
            # Calculate raw score
            raw_score = self.calculate_raw_score(symbol, gru_result, sentiment, volatility)
            
            # Convert to expected return and confidence
            expected_return, confidence = self.convert_to_expected_return(raw_score, volatility)
            
            # Determine recommendation
            if confidence >= 0.7 and expected_return > 0.02:
                recommendation = "Strong Buy"
            elif confidence >= 0.7 and expected_return < -0.02:
                recommendation = "Strong Sell"
            elif confidence >= 0.5 and expected_return > 0.01:
                recommendation = "Buy"
            elif confidence >= 0.5 and expected_return < -0.01:
                recommendation = "Sell"
            else:
                recommendation = "Hold"
            
            # Generate explanation
            reasons = []
            if df['Close'].iloc[-1] > df['ema_20'].iloc[-1]:
                reasons.append("Price trending above 20EMA")
            if sentiment > 0.3:
                reasons.append("Positive news sentiment")
            elif sentiment < -0.3:
                reasons.append("Negative news sentiment")
            if gru_result['confidence'] > 0.6:
                reasons.append("Strong technical signals")
            
            explanation = "; ".join(reasons) if reasons else "Mixed signals"
            
            # Risk level
            if volatility < 0.02:
                risk_level = "Low"
            elif volatility < 0.04:
                risk_level = "Medium"
            else:
                risk_level = "High"
            
            return {
                'symbol': symbol,
                'recommendation': recommendation,
                'expected_return': expected_return,
                'confidence': confidence,
                'risk_level': risk_level,
                'current_price': latest_price,
                'volatility': volatility,
                'explanation': explanation,
                'raw_score': raw_score,
                'gru_signals': gru_result,
                'sentiment': sentiment,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scouting {symbol}: {e}")
            return None
    
    def scout_all_assets(self, risk_preference: str = "Conservative") -> List[Dict]:
        """Scout all tracked assets and return ranked recommendations"""
        try:
            logger.info("Starting asset scouting")
            
            all_assets = self.crypto_assets + self.stock_assets
            recommendations = []
            
            for symbol in all_assets:
                result = self.scout_asset(symbol)
                if result:
                    recommendations.append(result)
            
            # Filter by risk preference
            if risk_preference == "Conservative":
                recommendations = [r for r in recommendations if r['risk_level'] in ['Low', 'Medium']]
            elif risk_preference == "Balanced":
                recommendations = [r for r in recommendations if r['risk_level'] in ['Low', 'Medium', 'High']]
            # Aggressive includes all
            
            # Sort by risk-adjusted expected return
            recommendations.sort(key=lambda x: x['expected_return'], reverse=True)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in scout_all_assets: {e}")
            return []
