const Redis = require('ioredis');

let client = null;
if (process.env.REDIS_URL) {
  client = new Redis(process.env.REDIS_URL);
  client.on('error', (e) => console.warn('Redis error', e));
}

module.exports = client;
