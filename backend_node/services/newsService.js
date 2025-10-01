/* News service
 - Fetch latest headlines using NewsAPI
 - Simple sentiment scoring (+1/0/-1)
 - Aggregate into sentimentIndex (-5..+5) depending on number of headlines
*/

const axios = require('axios');
const cache = require('../utils/cache');

const NEWS_KEY = process.env.NEWSAPI_KEY;
const NEWS_BASE = 'https://newsapi.org/v2/everything';
const CACHE_TTL = parseInt(process.env.CACHE_TTL_SECONDS || '10', 10);
const MOCK = process.env.MOCK_EXTERNAL === 'true';

function _mockHeadlines(query, limit) {
  const now = new Date().toISOString();
  const hs = [];
  for (let i = 0; i < limit; i++) {
    hs.push({ headline: `${query} mock headline ${i+1} sees slight gains`, source: 'MockNews', url: '', publishedAt: now });
  }
  return hs;
}

// naive sentiment word lists
const POS = ['gain', 'gains', 'rise', 'surge', 'bull', 'bullish', 'beat', 'positive', 'up', 'growth'];
const NEG = ['drop', 'drops', 'fall', 'decline', 'bear', 'bearish', 'miss', 'loss', 'down'];

function scoreHeadline(text) {
  if (!text) return 0;
  const t = text.toLowerCase();
  let score = 0;
  for (const w of POS) if (t.includes(w)) score += 1;
  for (const w of NEG) if (t.includes(w)) score -= 1;
  if (score > 0) return 1;
  if (score < 0) return -1;
  return 0;
}

async function fetchHeadlines(query = 'market', limit = 10) {
  const key = `news:${query}:${limit}`;
  const cached = await cache.get(key);
  if (cached) return cached;

  if (MOCK) {
    const m = _mockHeadlines(query, limit);
    await cache.set(key, m, CACHE_TTL);
    return m;
  }

  if (!NEWS_KEY) return [];

  try {
    const resp = await axios.get(NEWS_BASE, { params: { q: query, pageSize: limit, apiKey: NEWS_KEY, language: 'en', sortBy: 'publishedAt' } });
    const articles = (resp.data.articles || []).map(a => ({ headline: a.title, source: a.source?.name, url: a.url, publishedAt: a.publishedAt }));
    await cache.set(key, articles, CACHE_TTL);
    return articles;
  } catch (err) {
    return [];
  }
}

async function analyze(query = 'market', limit = 10) {
  const articles = await fetchHeadlines(query, limit);
  const scored = articles.map(a => ({ ...a, score: scoreHeadline(a.headline) }));
  // Sentiment index range roughly -limit..+limit; scale to -5..+5
  const sum = scored.reduce((s, a) => s + a.score, 0);
  const maxAbs = Math.max(1, limit);
  const index = Math.round((sum / maxAbs) * 5);
  return { sentimentIndex: Math.max(-5, Math.min(5, index)), headlines: scored };
}

module.exports = { fetchHeadlines, analyze };
