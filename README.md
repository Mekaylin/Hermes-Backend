# Hermes — Trading Companion (developer notes)

This README contains concise local developer instructions for running the backend and the full stack during development.

## Quick local backend (venv)

1. Create a virtualenv and activate it:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

2. Install minimal dependencies (development):

```bash
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
```

- Note: Some packages (pydantic-core, LightGBM) can require platform toolchains (Rust, libomp).
- Recommendation: Use Python 3.11 for best compatibility with SQLAlchemy/Alembic and many binary wheels used by the project. If you hit build errors, either:
- - Use Python 3.11 (prebuilt wheels are more common), or
- Use the Docker instructions below to run inside containers where build-time issues are avoided.

3. Run the backend in development mode:

```bash
cd backend
source venv/bin/activate
uvicorn backend.simple_main:app --host 0.0.0.0 --port 8000 --reload
```

4. ML model fallback: a small sklearn model has been saved to `backend/ml/artifacts/lightgbm_model.pkl` so `/predict` will work even if native LightGBM isn't available.

## Full stack (Docker compose)

This repo includes a `docker-compose.yml` that defines `backend`, `db` (Postgres), and `redis` services. Docker is recommended for full integration testing.

```bash
# from project root
docker compose up -d --build

# View backend logs
docker compose logs -f backend
```

Notes:
- The `backend` service reads `REDIS_URL` and `DATABASE_URL` from the environment. See `.env.example` for suggestions.
- If Docker isn't available on your machine, follow the venv instructions above instead.

## Optional: FinBERT sentiment

FinBERT support is optional. To enable:

1. Install transformers (and optionally sentencepiece):

```bash
pip install "transformers[sentencepiece]"
```

2. Set `FINBERT_MODEL` or `FINBERT_PATH` to a huggingface model id or local path:

```bash
export FINBERT_MODEL=ProsusAI/finbert
```

The sentiment endpoint will use FinBERT when configured; otherwise it uses a heuristic.

## Notes & Troubleshooting
- If `pip install -r requirements.txt` fails while building wheels (pydantic-core, LightGBM), use Docker or switch to Python 3.11/3.12.
- The project supports a Redis-backed distributed rate limiter. Ensure `REDIS_URL` points to a reachable Redis instance when running multiple backend workers.

## Next developer tasks
- Add Redis health-check during backend startup (pending)
- Improve training pipeline with real historical OHLCV data and retrain LightGBM/GRU models
- Wire Flutter frontend to backend endpoints and test end-to-end
# Hermes - AI Trading Companion

A comprehensive Flutter + FastAPI trading companion tool that provides real-time AI-powered market analysis and trading suggestions.

## 🚀 Features

- **Multi-Asset Support**: Forex, Commodities, Stocks, Indices, and Cryptocurrencies
- **AI-Powered Analysis**: Real-time Buy/Hold/Sell suggestions with confidence scores
- **Beginner-Friendly**: Clean interface with explanations for trading decisions
- **Advisory Only**: No direct trading - acts as your intelligent trading companion
- **Cost-Efficient**: Uses free-tier APIs and lightweight ML models
- **Cross-Platform**: Flutter app for iOS and Android

## 📁 Project Structure

```
├── frontend/          # Flutter mobile app
├── backend/           # FastAPI server with AI models
├── data/             # ML training scripts and data fetching
└── README.md
```

## 🛠️ Technology Stack

**Frontend (Flutter)**
- Flutter SDK 3.x
- Material Design 3
- Real-time WebSocket connections
- Cross-platform (iOS/Android)

**Backend (FastAPI)**
- FastAPI with async support
- ML Models: Random Forest, LightGBM
- SQLite/PostgreSQL for data storage
- WebSocket for real-time updates

**Data & AI**
- Free APIs: Binance, Yahoo Finance, Alpha Vantage
- Scikit-learn, LightGBM for ML
- Technical indicators with TA-Lib
- Sentiment analysis integration

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
flutter pub get
flutter run
```

## 📊 Asset Categories

- **Forex**: EUR/USD, GBP/USD, USD/JPY, etc.
- **Commodities**: Gold, Silver, Oil, Natural Gas
- **Stocks**: AAPL, TSLA, NVDA, GOOGL, etc.
- **Indices**: S&P 500, NASDAQ, Dow Jones
- **Crypto**: BTC/USDT, ETH/USDT, ADA/USDT, etc.

## 🤖 AI Features

- Real-time market analysis
- Buy/Hold/Sell recommendations
- Confidence scores (0-100%)
- Entry, target, and stop-loss suggestions
- Plain-language explanations
- Historical prediction tracking

## 📱 Mobile App Features

- Clean, intuitive interface
- Real-time price updates
- AI suggestion cards with color coding
- Asset search and filtering
- Trading explanations for beginners
- Cross-platform compatibility

## 🔧 Configuration

Create a `.env` file in the backend directory:
```
DATABASE_URL=sqlite:///./trading_companion.db
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
BINANCE_API_URL=https://api.binance.com
```

## 📈 Model Performance

The AI models are designed for educational and advisory purposes. Performance metrics are tracked and displayed in the admin dashboard.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This app is for educational and advisory purposes only. Always do your own research and never invest more than you can afford to lose.
