"""Download or verify FinBERT model weights for local use.

Usage:
  python backend/scripts/fetch_finbert.py --model ProsusAI/finbert

If `transformers` isn't installed this script will print instructions.
"""
import os
import argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', default='ProsusAI/finbert', help='HuggingFace model id')
    args = p.parse_args()

    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
    except Exception:
        print('transformers not installed. Install with: pip install "transformers[sentencepiece]"')
        return

    model_name = args.model
    cache_dir = os.path.expanduser('~/.cache/hermes/finbert')
    os.makedirs(cache_dir, exist_ok=True)
    print('Downloading FinBERT model:', model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)
    print('Saved to cache dir:', cache_dir)


if __name__ == '__main__':
    main()
