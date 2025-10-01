const express = require('express');
const router = express.Router();
const binance = require('../services/binanceService');

// GET /market-data/ticker?symbol=BTCUSDT
router.get('/ticker', async (req, res) => {
  try {
    const symbol = (req.query.symbol || 'BTCUSDT').toUpperCase();
    const data = await binance.getTicker(symbol);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch ticker' });
  }
});

// GET /market-data/klines?symbol=BTCUSDT&interval=1m&limit=500
router.get('/klines', async (req, res) => {
  try {
    const symbol = (req.query.symbol || 'BTCUSDT').toUpperCase();
    const interval = req.query.interval || '1m';
    const limit = parseInt(req.query.limit || '500', 10);
    const data = await binance.getKlines(symbol, interval, limit);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch klines' });
  }
});

module.exports = router;
