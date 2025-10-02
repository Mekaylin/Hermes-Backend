"""
Enhanced ML Models for Trading Signal Generation
Supports Random Forest, LightGBM, and ensemble methods
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import joblib
import os

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error
# initialize logger early so we can log from optional imports
logger = logging.getLogger(__name__)

# Make optional native libraries (lightgbm, talib) optional to avoid import-time failures
try:
    import lightgbm as lgb
except Exception:
    lgb = None
    logger.warning('lightgbm not available; LightGBMModel will be disabled or require a fallback')

# Technical Analysis (talib is optional; we provide light-weight fallbacks below)
try:
    import talib
except Exception:
    talib = None
    logger.warning('talib not available; using pandas-based technical indicator fallbacks')

# --- Lightweight fallbacks for talib functions (used when talib is not installed) ---
def _rsi(values, timeperiod=14):
    s = pd.Series(values).astype(float)
    delta = s.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1 / timeperiod, adjust=False).mean()
    roll_down = down.ewm(alpha=1 / timeperiod, adjust=False).mean()
    rs = roll_up / roll_down.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.values

def _ema(values, span):
    return pd.Series(values).ewm(span=span, adjust=False).mean().values

def _macd(values, fastperiod=12, slowperiod=26, signalperiod=9):
    fast = pd.Series(values).ewm(span=fastperiod, adjust=False).mean()
    slow = pd.Series(values).ewm(span=slowperiod, adjust=False).mean()
    macd = fast - slow
    signal = macd.ewm(span=signalperiod, adjust=False).mean()
    hist = macd - signal
    return macd.values, signal.values, hist.values

def _bbands(values, timeperiod=20, nbdevup=2, nbdevdn=2):
    s = pd.Series(values)
    ma = s.rolling(window=timeperiod).mean()
    sd = s.rolling(window=timeperiod).std()
    upper = ma + nbdevup * sd
    lower = ma - nbdevdn * sd
    return upper.values, ma.values, lower.values

def _stoch(high, low, close, k_period=14, d_period=3):
    high_roll = pd.Series(high).rolling(window=k_period).max()
    low_roll = pd.Series(low).rolling(window=k_period).min()
    k = 100 * (pd.Series(close) - low_roll) / (high_roll - low_roll)
    d = k.rolling(window=d_period).mean()
    return k.fillna(0).values, d.fillna(0).values

def _williams_r(high, low, close, timeperiod=14):
    high_roll = pd.Series(high).rolling(window=timeperiod).max()
    low_roll = pd.Series(low).rolling(window=timeperiod).min()
    wr = -100 * (high_roll - pd.Series(close)) / (high_roll - low_roll)
    return wr.fillna(0).values

def _obv(close, volume):
    c = pd.Series(close)
    v = pd.Series(volume)
    direction = c.diff().fillna(0).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    obv = (direction * v).cumsum()
    return obv.values

# Choose talib functions or fallbacks
def RSI(values, timeperiod=14):
    return talib.RSI(values, timeperiod=timeperiod) if talib is not None else _rsi(values, timeperiod)

def MACD(values):
    return talib.MACD(values) if talib is not None else _macd(values)

def BBANDS(values):
    return talib.BBANDS(values) if talib is not None else _bbands(values)

def STOCH(high, low, close):
    return talib.STOCH(high, low, close) if talib is not None else _stoch(high, low, close)

def WILLR(high, low, close):
    return talib.WILLR(high, low, close) if talib is not None else _williams_r(high, low, close)

def OBV(close, volume):
    return talib.OBV(close, volume) if talib is not None else _obv(close, volume)

def TRANGE(high, low, close):
    if talib is not None:
        return talib.TRANGE(high, low, close)
    # True range fallback
    high_s = pd.Series(high)
    low_s = pd.Series(low)
    close_s = pd.Series(close)
    tr1 = high_s - low_s
    tr2 = (high_s - close_s.shift(1)).abs()
    tr3 = (low_s - close_s.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.values

def ATR(high, low, close, timeperiod=14):
    tr = TRANGE(high, low, close)
    return pd.Series(tr).rolling(window=timeperiod).mean().values


from .data_fetcher_enhanced import MarketData, OHLCV, ohlcv_to_dataframe

logger = logging.getLogger(__name__)

class SignalType(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"

@dataclass
class TradingSignal:
    signal: SignalType
    confidence: float  # 0-100%
    entry_price: float
    target_price: float
    stop_loss: float
    reasoning: List[str]
    timestamp: datetime
    asset_symbol: str

@dataclass
class ModelPrediction:
    signal: SignalType
    confidence: float
    probability_scores: Dict[str, float]
    feature_importance: Dict[str, float]
    model_name: str

class FeatureEngineer:
    """Advanced feature engineering for trading models"""
    
    @staticmethod
    def create_technical_features(df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive technical analysis features"""

        df = df.copy()

        # Price features
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['price_volatility'] = df['returns'].rolling(window=20).std()

        # Moving averages
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
            df[f'price_vs_sma_{period}'] = df['close'] / df[f'sma_{period}'] - 1

        # RSI
        df['rsi'] = RSI(df['close'].values, timeperiod=14)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)

        # MACD
        macd, macd_signal, macd_hist = MACD(df['close'].values)
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_histogram'] = macd_hist
        df['macd_bullish'] = (df['macd'] > df['macd_signal']).astype(int)

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = BBANDS(df['close'].values)
        df['bb_upper'] = bb_upper
        df['bb_middle'] = bb_middle
        df['bb_lower'] = bb_lower
        df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
        df['bb_squeeze'] = (bb_upper - bb_lower) / bb_middle

        # Stochastic
        df['stoch_k'], df['stoch_d'] = STOCH(df['high'].values, df['low'].values, df['close'].values)

        # Williams %R
        df['williams_r'] = WILLR(df['high'].values, df['low'].values, df['close'].values)

        # ADX (Average Directional Index)
        # ADX not implemented in fallback; use a simple trend-strength proxy if talib missing
        if talib is not None and hasattr(talib, 'ADX'):
            df['adx'] = talib.ADX(df['high'].values, df['low'].values, df['close'].values)
        else:
            df['adx'] = (df['close'] - df['close'].rolling(window=14).min()) / (df['close'].rolling(window=14).max() - df['close'].rolling(window=14).min())

        # CCI (Commodity Channel Index)
        if talib is not None and hasattr(talib, 'CCI'):
            df['cci'] = talib.CCI(df['high'].values, df['low'].values, df['close'].values)
        else:
            tp = (df['high'] + df['low'] + df['close']) / 3
            ma = tp.rolling(window=20).mean()
            md = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
            df['cci'] = (tp - ma) / (0.015 * md)

        # Volume features
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['price_volume'] = df['close'] * df['volume']

            # On-Balance Volume
            df['obv'] = OBV(df['close'].values, df['volume'].values)

            # Volume Price Trend (use AD if available)
            if talib is not None and hasattr(talib, 'AD'):
                df['vpt'] = talib.AD(df['high'].values, df['low'].values, df['close'].values, df['volume'].values)
            else:
                df['vpt'] = (df['close'].pct_change().fillna(0) * df['volume']).cumsum()

        # Support and Resistance levels
        df['support'] = df['low'].rolling(window=20).min()
        df['resistance'] = df['high'].rolling(window=20).max()
        df['support_distance'] = (df['close'] - df['support']) / df['close']
        df['resistance_distance'] = (df['resistance'] - df['close']) / df['close']

        # Trend features
        df['higher_highs'] = (df['high'] > df['high'].shift(1)).astype(int)
        df['higher_lows'] = (df['low'] > df['low'].shift(1)).astype(int)
        df['uptrend'] = (df['higher_highs'] & df['higher_lows']).astype(int)

        # Market volatility
        df['true_range'] = TRANGE(df['high'].values, df['low'].values, df['close'].values)
        df['atr'] = ATR(df['high'].values, df['low'].values, df['close'].values)

        # Momentum indicators
        if talib is not None and hasattr(talib, 'MOM'):
            df['momentum'] = talib.MOM(df['close'].values, timeperiod=10)
        else:
            df['momentum'] = pd.Series(df['close']).diff(10).fillna(0).values

        if talib is not None and hasattr(talib, 'ROC'):
            df['rate_of_change'] = talib.ROC(df['close'].values, timeperiod=10)
        else:
            df['rate_of_change'] = pd.Series(df['close']).pct_change(10).fillna(0).values

        return df
    
    @staticmethod
    def create_target_variable(df: pd.DataFrame, future_periods: int = 5, threshold: float = 0.02) -> pd.DataFrame:
        """Create target variable for classification"""
        
        # Calculate future returns
        df['future_close'] = df['close'].shift(-future_periods)
        df['future_return'] = (df['future_close'] - df['close']) / df['close']
        
        # Create signal based on threshold
        conditions = [
            df['future_return'] > threshold,
            df['future_return'] < -threshold,
        ]
        choices = [SignalType.BUY.value, SignalType.SELL.value]
        
        df['signal'] = np.select(conditions, choices, default=SignalType.HOLD.value)
        
        return df

class RandomForestModel:
    """Random Forest model for trading signals"""
    
    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            class_weight='balanced',
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5
        )
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Prepare features for training/prediction"""
        
        # Select numeric features only
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove target and future columns
        exclude_columns = ['signal', 'future_close', 'future_return', 'open', 'high', 'low', 'close']
        feature_columns = [col for col in numeric_columns if col not in exclude_columns]
        
        # Handle missing values
        df_features = df[feature_columns].fillna(method='ffill').fillna(method='bfill')
        
        X = df_features.values
        y = None
        
        if 'signal' in df.columns:
            y = df['signal'].values
        
        self.feature_columns = feature_columns
        return X, y
        
    def train(self, df: pd.DataFrame) -> Dict:
        """Train the Random Forest model"""
        
        X, y = self.prepare_features(df)
        
        if y is None:
            raise ValueError("No target variable found for training")
        
        # Remove rows with NaN targets
        valid_indices = ~pd.isna(y)
        X = X[valid_indices]
        y = y[valid_indices]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.classifier.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.classifier, X_train_scaled, y_train, cv=5)
        
        self.is_trained = True
        
        return {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': dict(zip(self.feature_columns, self.classifier.feature_importances_))
        }
    
    def predict(self, df: pd.DataFrame) -> ModelPrediction:
        """Make prediction for new data"""
        
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X, _ = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # Get prediction and probabilities
        prediction = self.classifier.predict(X_scaled[-1:])
        probabilities = self.classifier.predict_proba(X_scaled[-1:])
        
        # Get class labels
        classes = self.classifier.classes_
        prob_dict = dict(zip(classes, probabilities[0]))
        
        # Calculate confidence as max probability
        confidence = max(probabilities[0]) * 100
        
        # Feature importance
        feature_importance = dict(zip(self.feature_columns, self.classifier.feature_importances_))
        
        return ModelPrediction(
            signal=SignalType(prediction[0]),
            confidence=confidence,
            probability_scores=prob_dict,
            feature_importance=feature_importance,
            model_name="RandomForest"
        )

class LightGBMModel:
    """LightGBM model for trading signals"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Prepare features for training/prediction"""
        
        # Select numeric features only
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove target and future columns
        exclude_columns = ['signal', 'future_close', 'future_return', 'open', 'high', 'low', 'close']
        feature_columns = [col for col in numeric_columns if col not in exclude_columns]
        
        # Handle missing values
        df_features = df[feature_columns].fillna(method='ffill').fillna(method='bfill')
        
        X = df_features.values
        y = None
        
        if 'signal' in df.columns:
            # Encode labels
            le = LabelEncoder()
            y = le.fit_transform(df['signal'].values)
            self.label_encoder = le
        
        self.feature_columns = feature_columns
        return X, y
        
    def train(self, df: pd.DataFrame) -> Dict:
        """Train the LightGBM model"""
        
        X, y = self.prepare_features(df)
        
        if y is None:
            raise ValueError("No target variable found for training")
        
        # Remove rows with NaN targets
        valid_indices = ~pd.isna(y)
        X = X[valid_indices]
        y = y[valid_indices]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Create LightGBM datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # Parameters
        params = {
            'objective': 'multiclass',
            'num_class': len(np.unique(y)),
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
        
        # Train model
        self.model = lgb.train(
            params,
            train_data,
            valid_sets=[test_data],
            num_boost_round=100,
            callbacks=[lgb.early_stopping(10), lgb.log_evaluation(0)]
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        accuracy = accuracy_score(y_test, y_pred_classes)
        
        self.is_trained = True
        
        # Feature importance
        feature_importance = dict(zip(self.feature_columns, self.model.feature_importance()))
        
        return {
            'accuracy': accuracy,
            'feature_importance': feature_importance
        }
    
    def predict(self, df: pd.DataFrame) -> ModelPrediction:
        """Make prediction for new data"""
        
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X, _ = self.prepare_features(df)
        
        # Get prediction
        probabilities = self.model.predict(X[-1:])
        prediction_idx = np.argmax(probabilities[0])
        
        # Convert back to signal
        signal_encoded = self.label_encoder.inverse_transform([prediction_idx])[0]
        
        # Calculate confidence
        confidence = max(probabilities[0]) * 100
        
        # Probability scores
        classes = self.label_encoder.classes_
        prob_dict = dict(zip(classes, probabilities[0]))
        
        # Feature importance
        feature_importance = dict(zip(self.feature_columns, self.model.feature_importance()))
        
        return ModelPrediction(
            signal=SignalType(signal_encoded),
            confidence=confidence,
            probability_scores=prob_dict,
            feature_importance=feature_importance,
            model_name="LightGBM"
        )

class EnsemblePredictor:
    """Ensemble predictor combining multiple models"""
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestModel(),
            'lightgbm': LightGBMModel()
        }
        self.is_trained = False
        
    def train(self, df: pd.DataFrame) -> Dict:
        """Train all models in ensemble"""
        
        # Engineer features
        df = FeatureEngineer.create_technical_features(df)
        df = FeatureEngineer.create_target_variable(df)
        
        results = {}
        
        for name, model in self.models.items():
            try:
                result = model.train(df)
                results[name] = result
                logger.info(f"Trained {name} with accuracy: {result['accuracy']:.3f}")
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                results[name] = {'error': str(e)}
        
        self.is_trained = True
        return results
    
    def predict(self, df: pd.DataFrame) -> TradingSignal:
        """Generate ensemble prediction"""
        
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        # Engineer features
        df = FeatureEngineer.create_technical_features(df)
        
        predictions = {}
        
        for name, model in self.models.items():
            if model.is_trained:
                try:
                    pred = model.predict(df)
                    predictions[name] = pred
                except Exception as e:
                    logger.error(f"Error predicting with {name}: {e}")
        
        if not predictions:
            raise ValueError("No models available for prediction")
        
        # Ensemble logic: weighted average of confidences
        signal_votes = {SignalType.BUY: 0, SignalType.HOLD: 0, SignalType.SELL: 0}
        total_confidence = 0
        reasoning = []
        
        for name, pred in predictions.items():
            weight = pred.confidence / 100
            signal_votes[pred.signal] += weight
            total_confidence += pred.confidence
            reasoning.append(f"{name}: {pred.signal.value} ({pred.confidence:.1f}%)")
        
        # Get final signal
        final_signal = max(signal_votes, key=signal_votes.get)
        ensemble_confidence = total_confidence / len(predictions)
        
        # Calculate price targets
        current_price = df['close'].iloc[-1]
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else current_price * 0.02
        
        if final_signal == SignalType.BUY:
            entry_price = current_price * 1.001  # Slight premium for market entry
            target_price = current_price * 1.02   # 2% profit target
            stop_loss = current_price * 0.98      # 2% stop loss
        elif final_signal == SignalType.SELL:
            entry_price = current_price * 0.999   # Slight discount for market entry
            target_price = current_price * 0.98   # 2% profit target (short)
            stop_loss = current_price * 1.02      # 2% stop loss (short)
        else:  # HOLD
            entry_price = current_price
            target_price = current_price
            stop_loss = current_price * 0.95      # Conservative stop loss
        
        return TradingSignal(
            signal=final_signal,
            confidence=ensemble_confidence,
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            reasoning=reasoning,
            timestamp=datetime.now(),
            asset_symbol=df.get('symbol', 'UNKNOWN')
        )
    
    def save_models(self, directory: str):
        """Save trained models to disk"""
        os.makedirs(directory, exist_ok=True)
        
        for name, model in self.models.items():
            if model.is_trained:
                model_path = os.path.join(directory, f"{name}_model.joblib")
                joblib.dump(model, model_path)
                logger.info(f"Saved {name} model to {model_path}")
    
    def load_models(self, directory: str):
        """Load trained models from disk"""
        
        for name in self.models.keys():
            model_path = os.path.join(directory, f"{name}_model.joblib")
            if os.path.exists(model_path):
                try:
                    self.models[name] = joblib.load(model_path)
                    logger.info(f"Loaded {name} model from {model_path}")
                except Exception as e:
                    logger.error(f"Error loading {name} model: {e}")
        
        self.is_trained = any(model.is_trained for model in self.models.values())
