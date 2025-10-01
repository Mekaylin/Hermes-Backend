// Environment configuration
export const config = {
  // API Configuration
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  appName: import.meta.env.VITE_APP_NAME || 'Hermes Trading Companion',
  
  // Firebase Configuration
  firebase: {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
  },
  
  // External API Keys
  newsApiKey: import.meta.env.VITE_NEWS_API_KEY,
  alphaVantageApiKey: import.meta.env.VITE_ALPHA_VANTAGE_API_KEY,
  
  // Development Settings
  debug: import.meta.env.VITE_DEBUG === 'true',
  mockMode: import.meta.env.VITE_MOCK_MODE === 'true',
  
  // Feature Flags
  features: {
    authentication: true,
    realTimeData: true,
    notifications: true,
    darkMode: true,
  }
};

// Validate required configuration
export const validateConfig = (): void => {
  const requiredFields = [
    'apiBaseUrl',
    'firebase.apiKey',
    'firebase.authDomain',
    'firebase.projectId'
  ];
  
  const missing = requiredFields.filter(field => {
    const value = field.split('.').reduce((obj: any, key) => obj?.[key], config);
    return !value || value === 'undefined';
  });
  
  if (missing.length > 0 && !config.mockMode) {
    console.warn('Missing required configuration:', missing);
    console.warn('Running in mock mode. Set environment variables for production.');
  }
};

export default config;
