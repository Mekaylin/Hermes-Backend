/// API configuration for Hermes backend
class AppConfig {
  // Backend API URLs
  static const String productionApiUrl = 'https://hermes-backend-5s2l.onrender.com';
  static const String localApiUrl = 'http://localhost:8000';
  
  // Use production by default, can be toggled for development
  static bool useLocalApi = false;
  
  static String get apiBaseUrl => useLocalApi ? localApiUrl : productionApiUrl;
  
  // API Endpoints
  static String get healthEndpoint => '$apiBaseUrl/health';
  static String get assetsEndpoint => '$apiBaseUrl/assets';
  static String marketDataEndpoint(String symbol) => '$apiBaseUrl/market/$symbol/current';
  static String get predictionsEndpoint => '$apiBaseUrl/predictions/generate';
  static String get sentimentEndpoint => '$apiBaseUrl/sentiment/analyze';
  
  // Firebase Collections
  static const String usersCollection = 'users';
  static const String portfoliosCollection = 'portfolios';
  static const String predictionsCollection = 'predictions';
  static const String watchlistsCollection = 'watchlists';
  static const String tradesCollection = 'trades';
}
