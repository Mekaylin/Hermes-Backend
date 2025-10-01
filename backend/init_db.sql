-- Fallback SQL to create the initial Hermes schema for local SQLite development
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS assets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  symbol TEXT NOT NULL UNIQUE,
  name TEXT,
  category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id INTEGER NOT NULL,
  timestamp DATETIME,
  open REAL,
  high REAL,
  low REAL,
  close REAL,
  volume REAL,
  FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_candles_timestamp ON candles(timestamp);

CREATE TABLE IF NOT EXISTS predictions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id INTEGER NOT NULL,
  timestamp DATETIME,
  signal TEXT,
  confidence REAL,
  entry REAL,
  target REAL,
  stop REAL,
  rationale TEXT,
  FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp);

CREATE TABLE IF NOT EXISTS news_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  asset_id INTEGER,
  timestamp DATETIME,
  source TEXT,
  headline TEXT,
  sentiment REAL,
  FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE SET NULL
);
-- SQL to initialize predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    asset VARCHAR(20) NOT NULL,
    signal VARCHAR(10) NOT NULL,
    confidence FLOAT NOT NULL,
    predicted_change FLOAT NOT NULL,
    model_version VARCHAR(10) NOT NULL
);
