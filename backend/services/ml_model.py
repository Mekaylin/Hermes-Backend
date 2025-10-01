"""ML model wrapper that loads a LightGBM model artifact when available.

If no artifact is found the class falls back to a simple heuristic.
"""
from typing import Dict, Any
import os
import pandas as pd
import joblib


class MLModel:
    def __init__(self, artifact_path: str = 'backend/ml/artifacts/lightgbm_model.pkl'):
        self.model = None
        self.artifact_path = artifact_path
        if os.path.exists(self.artifact_path):
            try:
                self.model = joblib.load(self.artifact_path)
            except Exception:
                self.model = None

    def predict(self, df: pd.DataFrame, indicators: pd.DataFrame, symbol: str, tf: str) -> Dict[str, Any]:
        """Return prediction dict. If model loaded, returns model probability as confidence.

        Output includes: signal, entry, target, stop, confidence, rationale
        """
        if self.model is not None and not df.empty:
            X = df[['close']].tail(1)
            try:
                proba = float(self.model.predict_proba(X)[:, 1][0])
            except Exception:
                proba = 0.5
            signal = 'BUY' if proba > 0.55 else ('SELL' if proba < 0.45 else 'HOLD')
            confidence = proba
            last_close = float(df['close'].iloc[-1])
            entry = last_close
            target = last_close * (1 + (proba - 0.5) * 0.1)
            stop = last_close * (1 - 0.02)
            rationale = f'LightGBM model score {proba:.3f}'
            return {
                'signal': signal,
                'entry': entry,
                'target': target,
                'stop': stop,
                'confidence': confidence,
                'rationale': rationale,
            }

        # Fallback heuristic
        last_close = float(df['close'].iloc[-1]) if not df.empty else 0.0
        signal = 'HOLD'
        confidence = 0.5
        rationale = 'Insufficient data or no model artifact'
        entry = last_close
        target = last_close
        stop = last_close

        return {
            'signal': signal,
            'entry': entry,
            'target': target,
            'stop': stop,
            'confidence': confidence,
            'rationale': rationale,
        }
