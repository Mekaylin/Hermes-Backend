# Hermes AI Market Analysis Flutter App

## Features
- Live market chart with AI trend overlay
- AI Trade Signal widget (buy/sell/hold, confidence, target price)
- News feed with sentiment color-coding
- Asset selector (default BTC-USD)
- Auto-refresh every minute

## Setup
1. Install Flutter: https://docs.flutter.dev/get-started/install
2. Run `flutter pub get` in this directory
3. Run the app: `flutter run`

## API
Connects to backend FastAPI endpoints:
- `/signal`
- `/history`
- `/news`
