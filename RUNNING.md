Quick run guide for Hermes (local dev)

Python backend (FastAPI, venv)

1. Activate venv

   source backend/venv/bin/activate

2. Optionally set DATABASE_URL to SQLite fallback (created by scripts/init_db.py):

   export DATABASE_URL="sqlite:///${PWD}/hermes_dev.sqlite3"

3. Start server

   python -m uvicorn backend.simple_main:app --host 127.0.0.1 --port 8000 --reload

4. Health

   curl http://127.0.0.1:8000/health

Node backend (mock mode)

1. Start mock server (no API keys required):

   cd backend_node
   npm install
   MOCK_EXTERNAL=true node server.js

2. Test

   curl "http://localhost:8080/ai-input?symbol=BTCUSDT"

Flutter frontend (serve web)

1. Point frontend to the backend by default it will use http://localhost:8080 (Node mock)
2. Start web server

   cd frontend
   flutter run -d web-server --web-hostname=localhost --web-port=3000

Notes
- If you want real data, populate `backend/.env` and `backend_node/.env` with API keys (AlphaVantage, NewsAPI, Binance) and run servers without `MOCK_EXTERNAL`.
- Redis and Postgres are optional for local dev; the project includes a SQLite fallback created by `backend/scripts/init_db.py`.

Optional: run Postgres and Redis via Docker (local dev)

1. Start via docker-compose (requires Docker):

   docker compose -f dev-docker-compose.yml up -d

2. Example env vars to use with the backends:

   export DATABASE_URL=postgresql+psycopg2://hermes:hermes_password@localhost:5432/hermes
   export REDIS_URL=redis://localhost:6379/0

See `docker/README.md` for more details.