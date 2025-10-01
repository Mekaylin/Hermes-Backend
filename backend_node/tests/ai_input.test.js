process.env.MOCK_EXTERNAL = 'true';
process.env.NODE_ENV = 'test';

const request = require('supertest');
const app = require('../server');

describe('GET /ai-input', () => {
  jest.setTimeout(20000);

  test('returns 200 and expected structure for symbol', async () => {
    const res = await request(app).get('/ai-input').query({ symbol: 'BTCUSDT' });
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('market');
    expect(res.body).toHaveProperty('indicators');
    expect(res.body).toHaveProperty('news');
  });
});
