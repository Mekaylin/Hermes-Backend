import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
POSTGRES_URL = os.getenv("POSTGRES_URL")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
