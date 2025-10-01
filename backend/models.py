"""Models with a graceful fallback when SQLAlchemy is unavailable.

When SQLAlchemy is present the ORM models are defined as usual. When it's
not available (e.g. incompatible Python version or not installed) this file
exposes minimal placeholder classes so the rest of the app can run in a
degraded mode without persistence.
"""
import enum
from . import db as _db


class AssetCategory(enum.Enum):
    crypto = "crypto"
    forex = "forex"
    stocks = "stocks"
    commodities = "commodities"


if getattr(_db, 'HAS_SQLALCHEMY', False):
    from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey
    from sqlalchemy.orm import relationship
    from .db import Base


    class Asset(Base):
        __tablename__ = 'assets'

        id = Column(Integer, primary_key=True, index=True)
        symbol = Column(String, unique=True, index=True, nullable=False)
        name = Column(String, nullable=True)
        category = Column(Enum(AssetCategory), nullable=False)


    class Candle(Base):
        __tablename__ = 'candles'

        id = Column(Integer, primary_key=True, index=True)
        asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
        timestamp = Column(DateTime, index=True)
        open = Column(Float)
        high = Column(Float)
        low = Column(Float)
        close = Column(Float)
        volume = Column(Float)

        asset = relationship('Asset')


    class Prediction(Base):
        __tablename__ = 'predictions'

        id = Column(Integer, primary_key=True, index=True)
        asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
        timestamp = Column(DateTime, index=True)
        signal = Column(String)
        confidence = Column(Float)
        entry = Column(Float)
        target = Column(Float)
        stop = Column(Float)
        rationale = Column(Text)

        asset = relationship('Asset')


    class NewsItem(Base):
        __tablename__ = 'news_items'

        id = Column(Integer, primary_key=True, index=True)
        asset_id = Column(Integer, ForeignKey('assets.id'), nullable=True)
        timestamp = Column(DateTime)
        source = Column(String)
        headline = Column(String)
        sentiment = Column(Float)

        asset = relationship('Asset')
else:
    # Minimal non-ORM placeholders used when SQLAlchemy can't be imported.
    class Asset:
        def __init__(self, symbol: str, name: str = None, category: AssetCategory = AssetCategory.stocks):
            self.id = None
            self.symbol = symbol
            self.name = name
            self.category = category


    class Candle:
        def __init__(self, asset_id=None, timestamp=None, open=0, high=0, low=0, close=0, volume=0):
            self.id = None
            self.asset_id = asset_id
            self.timestamp = timestamp
            self.open = open
            self.high = high
            self.low = low
            self.close = close
            self.volume = volume


    class Prediction:
        def __init__(self, asset_id=None, timestamp=None, signal=None, confidence=0.0, entry=0.0, target=0.0, stop=0.0, rationale=''):
            self.id = None
            self.asset_id = asset_id
            self.timestamp = timestamp
            self.signal = signal
            self.confidence = confidence
            self.entry = entry
            self.target = target
            self.stop = stop
            self.rationale = rationale


    class NewsItem:
        def __init__(self, asset_id=None, timestamp=None, source=None, headline=None, sentiment=0.0):
            self.id = None
            self.asset_id = asset_id
            self.timestamp = timestamp
            self.source = source
            self.headline = headline
            self.sentiment = sentiment
