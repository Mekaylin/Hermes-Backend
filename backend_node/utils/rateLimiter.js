// Simple token-bucket style rate limiter for in-process throttling.
// For AlphaVantage we enforce max requests per minute.

class RateLimiter {
  constructor(maxPerMinute) {
    this.maxPerMinute = maxPerMinute;
    this.tokens = maxPerMinute;
    this.lastRefill = Date.now();
  }

  _refill() {
    const now = Date.now();
    const elapsed = now - this.lastRefill;
    if (elapsed > 60000) {
      this.tokens = this.maxPerMinute;
      this.lastRefill = now;
    }
  }

  tryRemoveToken() {
    this._refill();
    if (this.tokens > 0) {
      this.tokens -= 1;
      return true;
    }
    return false;
  }
}

module.exports = RateLimiter;
