Hermes backend - local dev

Bring up services locally (requires Docker):

1) Build and run Postgres + Redis + backend (from repo root):

   docker compose up -d --build

2) Tail backend logs:

   docker compose logs -f backend

Run backend locally without Docker (venv must be prepared):

   cd backend
   source venv/bin/activate
   uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload

Notes:
- If you run on Python 3.13 you may encounter binary incompatibilities with
  some packages (pydantic/sqlalchemy). Use Python 3.11/3.12 for easiest
  compatibility or rebuild wheels locally.
# Hermes AI Market Analysis Backend

## Setup Instructions

1. Clone the repo and enter the backend folder:
   ```bash
   cd backend
   ```
2. Create a `.env` file with your API keys:
   ```
   ALPHA_VANTAGE_API_KEY=your_key
   BINANCE_API_KEY=your_key
   POSTGRES_URL=postgresql://user:pass@host:port/dbname
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

Optional: FinBERT (financial sentiment)
--------------------------------------
FinBERT can be used to improve sentiment analysis of news headlines. It is optional because
the model and transformers library are large. To enable FinBERT:

1. Install transformers in the backend venv:

```bash
source venv/bin/activate
pip install "transformers[sentencepiece]"
```

2. Download a FinBERT model into the local cache (we provide a helper):

```bash
python scripts/fetch_finbert.py --model ProsusAI/finbert
```

3. Set the `FINBERT_MODEL` or `FINBERT_PATH` env var to the model id or path, e.g.:

```bash
export FINBERT_MODEL=ProsusAI/finbert
# or the full local cache path
export FINBERT_PATH=$HOME/.cache/hermes/finbert
```

When enabled, the backend will try to use FinBERT for `services.sentiment.analyze_sentiment` and return higher-quality sentiment labels. If not available, the service falls back to a small keyword heuristic so the API continues working.


## Structure
- `main.py`: FastAPI app
- `config.py`: Loads .env config
- `scripts/`: Data fetch, training, sentiment analysis
- `CHANGES`: Log of all changes

## Docker
Docker setup will be added in the next step.

## FinBERT (optional)

To enable FinBERT sentiment analysis you need the `transformers` package and a FinBERT model. Use the provided helper to download weights into a cache directory:

```bash
# from repo root
python backend/scripts/fetch_finbert.py --model ProsusAI/finbert
```

Install transformers first if you haven't:

```bash
pip install "transformers[sentencepiece]"
```
