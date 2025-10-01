/* Alpha Vantage service
 - Fetch indicators (RSI, MACD, SMA/EMA) via AlphaVantage
 - Throttles calls to respect free-tier limits (5/min)
 - Caches results for 60s
*/

const axios = require('axios');
const cache = require('../utils/cache');
const RateLimiter = require('../utils/rateLimiter');

const ALPHA_KEY = process.env.ALPHAVANTAGE_KEY;
const ALPHA_BASE = 'https://www.alphavantage.co/query';
const CACHE_TTL = parseInt(process.env.ALPHA_CACHE_TTL_SECONDS || '60', 10);
const ALPHA_RATE = parseInt(process.env.ALPHA_RATE_PER_MIN || '5', 10);

const limiter = new RateLimiter(ALPHA_RATE);
const MOCK = process.env.MOCK_EXTERNAL === 'true';

function _mockIndicator(fn, symbol) {
  // return a simple shaped object similar to AlphaVantage's payload
  if (fn === 'RSI') {
    return { 'Meta Data': { '2: Symbol': symbol }, 'Technical Analysis: RSI': { '2025-01-01': { 'RSI': '55.00' } } };
  }
  if (fn === 'SMA' || fn === 'EMA') {
    return { 'Meta Data': { '2: Symbol': symbol }, ['Technical Analysis: ' + fn]: { '2025-01-01': { 'SMA': '26000.00' } } };
  }
  if (fn === 'MACD') {
    return { 'Meta Data': { '2: Symbol': symbol }, 'Technical Analysis: MACD': { '2025-01-01': { 'MACD': '1.23', 'MACD_Hist': '0.1', 'MACD_Signal': '1.13' } } };
  }
  return { 'Meta Data': { '2: Symbol': symbol } };
}

async function fetchIndicator(functionName, symbol, interval) {
  const cacheKey = `alpha:${functionName}:${symbol}:${interval}`;
  const cached = await cache.get(cacheKey);
  if (cached) return cached;

  // Throttle
  if (!limiter.tryRemoveToken()) {
    // Too many requests, return null to indicate temporarily unavailable
    return null;
  }

  if (MOCK) {
    const m = _mockIndicator(functionName, symbol);
    await cache.set(cacheKey, m, CACHE_TTL);
    return m;
  }

  const params = {
    function: functionName,
    symbol,
    interval,
    apikey: ALPHA_KEY,
  };

  try {
    const resp = await axios.get(ALPHA_BASE, { params });
    await cache.set(cacheKey, resp.data, CACHE_TTL);
    return resp.data;
  } catch (err) {
    // On error, do not crash; return null
    return null;
  }
}

async function getRSI(symbol, interval = 'daily') {
  // AlphaVantage uses RSI function with time series; use function=RSI
  const data = await fetchIndicator('RSI', symbol, interval);
  return data;
}

async function getSMA(symbol, interval = 'daily') {
  const data = await fetchIndicator('SMA', symbol, interval);
  return data;
}

async function getEMA(symbol, interval = 'daily') {
  const data = await fetchIndicator('EMA', symbol, interval);
  return data;
}

async function getMACD(symbol) {
  const data = await fetchIndicator('MACD', symbol, '');
  return data;
}

module.exports = { getRSI, getSMA, getEMA, getMACD };
