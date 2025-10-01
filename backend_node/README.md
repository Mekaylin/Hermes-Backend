Hermes Node backend

Quick start:

1. Copy `.env.example` to `.env` and fill keys

2. Install

```bash
cd backend_node
npm install
```

3. Run

```bash
npm run dev
```

Available endpoints:
- GET /market-data/ticker?symbol=BTCUSDT
- GET /market-data/klines?symbol=BTCUSDT&interval=1m&limit=500
- GET /indicators/rsi?symbol=IBM&interval=daily
- GET /news-sentiment?query=bitcoin&limit=10
- GET /ai-input?symbol=BTCUSDT

Notes:
- This backend uses in-memory cache. Deploy with Redis for production.
- Be careful with free-tier limits (AlphaVantage 5/min). A process-level RateLimiter is used.

Mock mode

Set `MOCK_EXTERNAL=true` to run the server without contacting external APIs. This is useful for local frontend integration or when API keys / network access are unavailable. Example:

MOCK_EXTERNAL=true node server.js

The mock mode returns canned tickers, klines, indicators and news headlines.
