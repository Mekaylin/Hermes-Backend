import os
import requests
from config import ALPHA_VANTAGE_API_KEY, BINANCE_API_KEY

def fetch_alpha_vantage_ohlcv(symbol="BTCUSD", interval="1min"):
	url = f"https://www.alphavantage.co/query"
	params = {
		"function": "TIME_SERIES_INTRADAY",
		"symbol": symbol,
		"interval": interval,
		"apikey": ALPHA_VANTAGE_API_KEY
	}
	r = requests.get(url, params=params)
	return r.json()

def fetch_binance_ohlcv(symbol="BTCUSDT", interval="1m"):
	url = f"https://api.binance.com/api/v3/klines"
	params = {
		"symbol": symbol,
		"interval": interval,
		"limit": 100
	}
	r = requests.get(url, params=params)
	return r.json()


def fetch_news(symbol="BTC"):
	# Example using NewsAPI (replace with your API key)
	NEWS_API_KEY = os.getenv("NEWS_API_KEY")
	url = f"https://newsapi.org/v2/everything"
	params = {
		"q": symbol,
		"sortBy": "publishedAt",
		"apiKey": NEWS_API_KEY,
		"language": "en"
	}
	r = requests.get(url, params=params)
	return r.json()

# Technical indicators
import pandas as pd

def calculate_ema(df, period=14, column='close'):
	return df[column].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14, column='close'):
	delta = df[column].diff()
	gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
	loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
	rs = gain / loss
	rsi = 100 - (100 / (1 + rs))
	return rsi

def calculate_macd(df, column='close', fast=12, slow=26, signal=9):
	ema_fast = df[column].ewm(span=fast, adjust=False).mean()
	ema_slow = df[column].ewm(span=slow, adjust=False).mean()
	macd = ema_fast - ema_slow
	signal_line = macd.ewm(span=signal, adjust=False).mean()
	return macd, signal_line

def calculate_bollinger_bands(df, period=20, column='close'):
	sma = df[column].rolling(window=period).mean()
	std = df[column].rolling(window=period).std()
	upper_band = sma + (std * 2)
	lower_band = sma - (std * 2)
	return upper_band, lower_band
