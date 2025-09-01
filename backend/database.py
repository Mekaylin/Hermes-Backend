import os
import json
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# For now, use file-based storage instead of PostgreSQL
PREDICTIONS_FILE = "predictions.json"

def load_predictions() -> List[Dict]:
    """Load predictions from file"""
    try:
        if os.path.exists(PREDICTIONS_FILE):
            with open(PREDICTIONS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading predictions: {e}")
        return []

def save_predictions(predictions: List[Dict]):
    """Save predictions to file"""
    try:
        with open(PREDICTIONS_FILE, 'w') as f:
            json.dump(predictions, f, default=str, indent=2)
    except Exception as e:
        logger.error(f"Error saving predictions: {e}")

def store_prediction(timestamp, asset, signal, confidence, predicted_change, model_version):
    """Store a new prediction"""
    try:
        predictions = load_predictions()
        
        prediction = {
            "id": len(predictions) + 1,
            "timestamp": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
            "asset": asset,
            "signal": signal,
            "confidence": float(confidence),
            "predicted_change": float(predicted_change),
            "model_version": model_version
        }
        
        predictions.append(prediction)
        save_predictions(predictions)
        
        logger.info(f"Stored prediction for {asset}: {signal}")
        
    except Exception as e:
        logger.error(f"Error storing prediction: {e}")

def get_predictions(asset=None, limit=100):
    """Get historical predictions"""
    try:
        predictions = load_predictions()
        
        if asset:
            predictions = [p for p in predictions if p.get('asset') == asset]
        
        # Sort by timestamp descending and limit
        predictions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return predictions[:limit]
        
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return []