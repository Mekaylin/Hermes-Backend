// Simple in-memory cache with TTL. Keeps lightweight for production use.
// Note: For multiple-instance deployment use Redis or another central cache.

const _cache = new Map();
const redis = require('./redisClient');

async function set(key, value, ttlSeconds) {
  if (redis) {
    try {
      await redis.set(key, JSON.stringify(value), 'EX', ttlSeconds);
      return;
    } catch (e) {
      // fall back to memory
    }
  }
  const expiresAt = Date.now() + ttlSeconds * 1000;
  _cache.set(key, { value, expiresAt });
}

async function get(key) {
  if (redis) {
    try {
      const v = await redis.get(key);
      if (v === null) return null;
      return JSON.parse(v);
    } catch (e) {
      // fallback to memory
    }
  }
  const entry = _cache.get(key);
  if (!entry) return null;
  if (Date.now() > entry.expiresAt) {
    _cache.delete(key);
    return null;
  }
  return entry.value;
}

async function del(key) {
  if (redis) {
    try {
      await redis.del(key);
      return;
    } catch (e) {
      // fallback
    }
  }
  _cache.delete(key);
}

module.exports = { set, get, del };
