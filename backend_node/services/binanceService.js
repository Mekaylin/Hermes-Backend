/* Binance service
 - fetch ticker and klines
 - caches results for short TTL to avoid rate limit
*/

const axios = require('axios');
const cache = require('../utils/cache');

const BASE = process.env.BINANCE_BASE || 'https://api.binance.com';
const CACHE_TTL = parseInt(process.env.CACHE_TTL_SECONDS || '10', 10);
const MOCK = process.env.MOCK_EXTERNAL === 'true';

function _mockTicker(symbol) {
  return {
    symbol,
    price: 43000.5,
    priceChangePercent: 2.1,
    volume: 123456.78
  };
}

function _mockKlines(interval, limit) {
  const now = Date.now();
  const ms = { '1m': 60000, '5m': 300000, '1h': 3600000, '1d': 86400000 }[interval] || 60000;
  const arr = [];
  let price = 43000;
  for (let i = 0; i < Math.min(limit, 200); i++) {
    const open = price + (Math.random() - 0.5) * 50;
    const close = open + (Math.random() - 0.5) * 50;
    arr.push({ openTime: now - (limit - i) * ms, open, high: Math.max(open, close) + 10, low: Math.min(open, close) - 10, close, volume: Math.random() * 1000, closeTime: now - (limit - i - 1) * ms });
    price = close;
  }
  return arr;
}

async function _axiosGetWithRetry(url, params, attempts = 3, delayMs = 500) {
  let lastErr = null;
  for (let i = 0; i < attempts; i++) {
    try {
      const resp = await axios.get(url, { params, timeout: 5000 });
      return resp;
    } catch (e) {
      lastErr = e;
      // exponential backoff
      await new Promise(r => setTimeout(r, delayMs * Math.pow(2, i)));
    }
  }
  throw lastErr;
}

async function getTicker(symbol) {
  // Binance uses symbol like BTCUSDT
  const key = `ticker:${symbol}`;
  if (MOCK) {
    const m = _mockTicker(symbol);
    await cache.set(key, m, CACHE_TTL);
    return m;
  }
  const cached = await cache.get(key);
  if (cached) return cached;

  const url = `${BASE}/api/v3/ticker/24hr`;
  try {
    const resp = await _axiosGetWithRetry(url, { symbol });
    const data = {
      symbol: resp.data.symbol,
      price: parseFloat(resp.data.lastPrice),
      priceChangePercent: parseFloat(resp.data.priceChangePercent),
      volume: parseFloat(resp.data.volume)
    };
    await cache.set(key, data, CACHE_TTL);
    return data;
  } catch (err) {
    // Provide useful error object rather than throwing raw
    return { error: 'binance_error', message: err.message || String(err) };
  }
}

async function getKlines(symbol, interval = '1m', limit = 500) {
  const key = `klines:${symbol}:${interval}:${limit}`;
  if (MOCK) {
    const m = _mockKlines(interval, limit);
    await cache.set(key, m, CACHE_TTL);
    return m;
  }
  const cached = await cache.get(key);
  if (cached) return cached;

  const url = `${BASE}/api/v3/klines`;
  try {
    const resp = await _axiosGetWithRetry(url, { symbol, interval, limit });
    // Convert klines to OHLCV objects for charts
    const series = resp.data.map(k => ({
      openTime: k[0],
      open: parseFloat(k[1]),
      high: parseFloat(k[2]),
      low: parseFloat(k[3]),
      close: parseFloat(k[4]),
      volume: parseFloat(k[5]),
      closeTime: k[6]
    }));

    await cache.set(key, series, CACHE_TTL);
    return series;
  } catch (err) {
    return { error: 'binance_error', message: err.message || String(err) };
  }
}

module.exports = { getTicker, getKlines };
