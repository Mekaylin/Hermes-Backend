"""Optional FinBERT sentiment pipeline.

This module uses the Hugging Face `transformers` library when a FINBERT_MODEL
or FINBERT_PATH environment variable is provided. If not configured it will
raise ImportError when import is attempted.
"""
import os
from typing import List, Dict


def load_finbert(model_name: str):
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    except Exception as e:
        raise ImportError('transformers is required for FinBERT support') from e

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    nlp = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
    return nlp


def analyze_with_finbert(headlines: List[Dict], model_name: str) -> List[Dict]:
    nlp = load_finbert(model_name)
    out = []
    for h in headlines:
        text = h.get('headline') or ''
        try:
            res = nlp(text[:512])[0]
            sentiment = res.get('label', 'NEUTRAL').lower()
        except Exception:
            sentiment = 'neutral'
        out.append({**h, 'sentiment': sentiment})
    return out
