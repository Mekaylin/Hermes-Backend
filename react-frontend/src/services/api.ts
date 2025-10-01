import axios from 'axios';
import config from '../config';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const api = {
  // Health check
  health: () => apiClient.get('/health'),
  
  // Market data
  market: {
    getMarketData: (symbol?: string) => 
      apiClient.get('/market', { params: { symbol } }),
    getMarketOverview: () => 
      apiClient.get('/market/overview'),
  },
  
  // Predictions
  predictions: {
    generate: (data?: any) => 
      apiClient.post('/predictions/generate', data),
    getHistory: () => 
      apiClient.get('/predictions/history'),
  },
  
  // News
  news: {
    getLatest: (limit = 10) => 
      apiClient.get('/news', { params: { limit } }),
    getSentiment: (symbol: string) => 
      apiClient.get(`/news/sentiment/${symbol}`),
  },
  
  // Recommendations
  recommendations: {
    get: (symbol?: string) => 
      apiClient.get('/recommendations', { params: { symbol } }),
  },
};

// Mock data for development
export const mockData = {
  health: {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    redis: { available: false },
    finbert_available: false,
  },
  
  marketData: {
    symbol: 'BTCUSDT',
    price: 43250.50,
    change: 1250.75,
    changePercent: 2.98,
    volume: 1234567.89,
    timestamp: new Date().toISOString(),
  },
  
  prediction: {
    symbol: 'BTCUSDT',
    signal: 'BUY',
    confidence: 78.5,
    entry_price: 43000.50,
    target_price: 45000.00,
    stop_loss: 41000.00,
    reasoning: ['Technical indicators show bullish momentum', 'Market sentiment is positive'],
    timestamp: new Date().toISOString(),
    recommendation: 'Consider buying with high confidence. Target: $45000.00, Stop Loss: $41000.00',
  },
  
  news: [
    {
      id: '1',
      title: 'Bitcoin Reaches New Monthly High',
      summary: 'Bitcoin continues its upward trajectory amid institutional adoption.',
      url: 'https://example.com/news/1',
      publishedAt: new Date().toISOString(),
      sentiment: 'positive',
    },
    {
      id: '2',
      title: 'Market Analysis: Crypto Trends for Q4',
      summary: 'Analysts predict continued growth in the cryptocurrency market.',
      url: 'https://example.com/news/2',
      publishedAt: new Date().toISOString(),
      sentiment: 'neutral',
    },
  ],
};

export default apiClient;
