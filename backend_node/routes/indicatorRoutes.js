const express = require('express');
const router = express.Router();
const alpha = require('../services/alphaService');

// GET /indicators/rsi?symbol=IBM&interval=daily
router.get('/rsi', async (req, res) => {
  try {
    const symbol = (req.query.symbol || 'IBM').toUpperCase();
    const interval = req.query.interval || 'daily';
    const data = await alpha.getRSI(symbol, interval);
    res.json({ symbol, indicator: 'RSI', data });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch RSI' });
  }
});

router.get('/ema', async (req, res) => {
  try {
    const symbol = (req.query.symbol || 'IBM').toUpperCase();
    const interval = req.query.interval || 'daily';
    const data = await alpha.getEMA(symbol, interval);
    res.json({ symbol, indicator: 'EMA', data });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch EMA' });
  }
});

router.get('/macd', async (req, res) => {
  try {
    const symbol = (req.query.symbol || 'IBM').toUpperCase();
    const data = await alpha.getMACD(symbol);
    res.json({ symbol, indicator: 'MACD', data });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch MACD' });
  }
});

module.exports = router;
