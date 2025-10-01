const express = require('express');
const router = express.Router();
const binance = require('../services/binanceService');
const alpha = require('../services/alphaService');
const news = require('../services/newsService');
const MOCK = process.env.MOCK_EXTERNAL === 'true';

// GET /ai-input?symbol=BTCUSDT
router.get('/', async (req, res) => {
  try {
    const symbol = (req.query.symbol || 'BTCUSDT').toUpperCase();
    const interval = req.query.interval || '1h';

    // gather market summary
    const ticker = await binance.getTicker(symbol).catch(() => null);
    const klines = await binance.getKlines(symbol, interval, 100).catch(() => []);

    // indicators (best-effort)
    const rsi = await alpha.getRSI(symbol.replace(/USDT|USD$/, ''), 'daily').catch(() => null);
    const macd = await alpha.getMACD(symbol.replace(/USDT|USD$/, '')).catch(() => null);

    // news sentiment
    const newsRes = await news.analyze(symbol.replace(/USDT|USD$/, ''), 10).catch(() => ({ sentimentIndex: 0, headlines: [] }));

    const payload = {
      market: { ticker, recentKlines: klines.slice(-100) },
      indicators: { rsi, macd },
      news: newsRes
    };

    res.json(payload);
  } catch (err) {
    res.status(500).json({ error: 'Failed to build AI input payload' });
  }
});

module.exports = router;
