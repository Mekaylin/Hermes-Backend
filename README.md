# Hermes - AI Trading Companion

A Flutter + FastAPI mobile trading companion app that provides real-time AI-powered market analysis and trading suggestions.

## 🚀 Features

- **Multi-Asset Support**: Forex, Commodities, Stocks, Indices, and Cryptocurrencies
- **AI-Powered Analysis**: Real-time Buy/Hold/Sell suggestions with confidence scores
- **Beginner-Friendly**: Clean interface with explanations for trading decisions
- **Advisory Only**: No direct trading - acts as your intelligent trading companion
- **Cost-Efficient**: Uses free-tier APIs and lightweight ML models
- **Mobile & Desktop**: Flutter app for iOS, Android, and macOS

## 📁 Project Structure

```
├── frontend/          # Flutter app (iOS, Android, macOS)
├── backend/           # FastAPI server with AI models
├── data/             # ML training scripts and data fetching
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- **Flutter**: 3.35.2+ ([Install Flutter](https://flutter.dev/docs/get-started/install))
- **Python**: 3.11+ ([Install Python](https://www.python.org/downloads/))
- **Firebase Account**: For authentication and Firestore database
- **Node.js**: For Firebase CLI (optional but recommended)

### Backend Setup

1. Create and activate a virtual environment:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:

```bash
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
```

3. Run the backend:

```bash
uvicorn backend.simple_main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at `http://localhost:8000`

**Production Backend**: `https://hermes-backend-5s2l.onrender.com`

### Flutter App Setup

1. Navigate to the Flutter app:

```bash
cd frontend
```

2. Install dependencies:

```bash
flutter pub get
```

3. Configure Firebase (see [FLUTTER_SETUP.md](FLUTTER_SETUP.md) for detailed instructions):

```bash
# Install FlutterFire CLI
dart pub global activate flutterfire_cli

# Configure Firebase for your project
flutterfire configure --project=hermes
```

4. Run the app:

```bash
# Web
flutter run -d chrome

# iOS
flutter run -d ios

# Android
flutter run -d android

# macOS
flutter run -d macos
```

## 📚 Documentation

- **[FLUTTER_SETUP.md](FLUTTER_SETUP.md)**: Complete Flutter + Firebase setup guide
- **[PRODUCTION_DEPLOYED.md](PRODUCTION_DEPLOYED.md)**: Backend deployment information
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Deployment instructions and configuration

## 🔧 Development

### Running the Full Stack Locally

1. Start the backend (in one terminal):
```bash
cd backend
source venv/bin/activate
uvicorn backend.simple_main:app --host 0.0.0.0 --port 8000 --reload
```

2. Start the Flutter app (in another terminal):
```bash
cd frontend
flutter run -d chrome  # or your preferred platform
```

### Docker Support (Optional)

For full integration testing with Postgres and Redis:

```bash
docker compose up -d --build
docker compose logs -f backend
```

## 🏗️ Architecture

- **Frontend**: Flutter (all platforms) with Firebase for auth and Firestore for data persistence
- **Backend**: FastAPI (Python) with AI/ML models for market predictions
- **Database**: Firestore for user data, portfolios, watchlists
- **Deployment**: Backend on Render, Flutter app can be deployed to app stores or web hosting

## � Firebase Services Used

- **Firebase Auth**: User authentication (email/password, Google sign-in)
- **Cloud Firestore**: NoSQL database for user data
- **Firebase Analytics**: App usage tracking (optional)

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
