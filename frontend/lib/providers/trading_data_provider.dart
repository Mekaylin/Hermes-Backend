import 'package:flutter/foundation.dart';
import '../models/trading_data.dart';
import '../services/api_service.dart';

class TradingDataProvider extends ChangeNotifier {
  ApiService _apiService;
  
  // State
  List<Asset> _allAssets = [];
  Asset? _selectedAsset;
  MarketData? _marketData;
  TradingSignal? _tradingSignal;
  bool _isLoading = false;
  String? _error;
  
  // Getters
  List<Asset> get allAssets => _allAssets;
  Asset? get selectedAsset => _selectedAsset;
  MarketData? get marketData => _marketData;
  TradingSignal? get tradingSignal => _tradingSignal;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  TradingDataProvider(this._apiService) {
    _loadAssets();
  }

  set apiService(ApiService svc) {
    _apiService = svc;
    // potential reconfiguration when apiService changes
    notifyListeners();
  }
  
  // Load all available assets
  Future<void> _loadAssets() async {
    try {
      _setLoading(true);
      _setError(null);
      
      final assets = await _apiService.getAssets();
      _allAssets = assets;
      
      notifyListeners();
    } catch (e) {
      _setError('Failed to load assets: $e');
    } finally {
      _setLoading(false);
    }
  }
  
  // Search assets by query
  List<Asset> searchAssets(String query) {
    if (query.isEmpty) return [];
    
    final lowerQuery = query.toLowerCase();
    return _allAssets.where((asset) {
      return asset.symbol.toLowerCase().contains(lowerQuery) ||
             asset.name.toLowerCase().contains(lowerQuery);
    }).take(10).toList();
  }
  
  // Get assets by category
  List<Asset> getAssetsByCategory(AssetCategory category) {
    return _allAssets.where((asset) => asset.category == category).toList();
  }
  
  // Set selected asset
  void setSelectedAsset(Asset asset) {
    _selectedAsset = asset;
    _marketData = null;
    _tradingSignal = null;
    notifyListeners();
  }
  
  // Set market data
  void setMarketData(MarketData data) {
    _marketData = data;
    notifyListeners();
  }
  
  // Set trading signal
  void setTradingSignal(TradingSignal signal) {
    _tradingSignal = signal;
    notifyListeners();
  }
  
  // Set loading state
  void setLoading(bool loading) {
    _setLoading(loading);
  }
  
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  // Set error
  void setError(String? error) {
    _setError(error);
  }
  
  void _setError(String? error) {
    _error = error;
    notifyListeners();
  }
  
  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
  
  // Refresh data for current asset
  Future<void> refreshCurrentAsset() async {
    if (_selectedAsset == null) return;
    
    try {
      _setLoading(true);
      _setError(null);
      
      // Load fresh market data
      final marketData = await _apiService.getCurrentMarketData(_selectedAsset!.symbol);
      setMarketData(marketData);
      
      // Generate new trading signal
      final signal = await _apiService.generatePrediction(symbol: _selectedAsset!.symbol);
      setTradingSignal(signal);
      
    } catch (e) {
      _setError('Failed to refresh data: $e');
    } finally {
      _setLoading(false);
    }
  }
  
  // Get popular assets (top 10 by some criteria)
  List<Asset> getPopularAssets() {
    // Return a mix of popular assets from different categories
    final popular = <Asset>[];
    
    // Add some crypto
    final crypto = getAssetsByCategory(AssetCategory.crypto);
    if (crypto.isNotEmpty) popular.addAll(crypto.take(3));
    
    // Add some forex
    final forex = getAssetsByCategory(AssetCategory.forex);
    if (forex.isNotEmpty) popular.addAll(forex.take(3));
    
    // Add some stocks
    final stocks = getAssetsByCategory(AssetCategory.stocks);
    if (stocks.isNotEmpty) popular.addAll(stocks.take(2));
    
    // Add some indices
    final indices = getAssetsByCategory(AssetCategory.indices);
    if (indices.isNotEmpty) popular.addAll(indices.take(2));
    
    return popular;
  }
  
  // Generate prediction for current asset
  Future<void> generatePrediction() async {
    if (_selectedAsset == null) return;
    
    try {
      _setLoading(true);
      _setError(null);
      
      final signal = await _apiService.generatePrediction(
        symbol: _selectedAsset!.symbol,
      );
      setTradingSignal(signal);
      
    } catch (e) {
      _setError('Failed to generate prediction: $e');
    } finally {
      _setLoading(false);
    }
  }
  
  // Get asset by symbol
  Asset? getAssetBySymbol(String symbol) {
    try {
      return _allAssets.firstWhere(
        (asset) => asset.symbol.toLowerCase() == symbol.toLowerCase(),
      );
    } catch (e) {
      return null;
    }
  }
  
  // Reload all data
  Future<void> reload() async {
    await _loadAssets();
    if (_selectedAsset != null) {
      await refreshCurrentAsset();
    }
  }
}
