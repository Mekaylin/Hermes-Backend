const express = require('express');
const router = express.Router();
const news = require('../services/newsService');

// GET /news-sentiment?query=bitcoin&limit=10
router.get('/', async (req, res) => {
  try {
    const query = req.query.query || 'market';
    const limit = parseInt(req.query.limit || '10', 10);
    const result = await news.analyze(query, limit);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch news sentiment' });
  }
});

module.exports = router;
