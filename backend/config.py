from __future__ import annotations
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional
from pydantic import ConfigDict


class Settings(BaseSettings):
    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_API_TYPE: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_API_VERSION: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = None

    # Other defaults
    OPENAI_TIMEOUT: int = 30
    OPENAI_TEMPERATURE: float = 0.3
    OPENAI_MAX_TOKENS: int = 1500

    model_config = ConfigDict(env_file=str(Path(__file__).parent / ".env"), extra='ignore')


settings = Settings()
import os
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
POSTGRES_URL = os.getenv("POSTGRES_URL")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
