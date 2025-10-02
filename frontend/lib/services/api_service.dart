import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/trading_data.dart';
import '../config/app_config.dart';

class ApiService {
  final String baseUrl;

  // Use production backend by default (can be toggled in AppConfig)
  ApiService({String? baseUrl}) : baseUrl = baseUrl ?? AppConfig.apiBaseUrl;

  // Get all available assets
  Future<List<Asset>> getAssets() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/assets/search'));
      
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        final List<dynamic> assetsList = data['assets'] as List;
        
        return assetsList.map((asset) => Asset(
          symbol: asset['symbol'],
          name: asset['name'],
          category: _parseCategory(asset['category']),
          exchange: asset['exchange'] ?? 'Unknown',
          description: asset['description'] ?? '',
        )).toList();
      } else {
        throw Exception('Failed to load assets: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching assets: $e');
    }
  }

  // Search assets by query
  Future<List<Asset>> searchAssets({String query = ''}) async {
    try {
      final assets = await getAssets();
      if (query.isEmpty) return assets;
      
      final lowerQuery = query.toLowerCase();
      return assets.where((asset) {
        return asset.symbol.toLowerCase().contains(lowerQuery) ||
               asset.name.toLowerCase().contains(lowerQuery);
      }).toList();
    } catch (e) {
      throw Exception('Error searching assets: $e');
    }
  }

  // Get current market data for a symbol
  Future<MarketData> getCurrentMarketData(String symbol) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/market/$symbol/current'));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return MarketData(
          symbol: symbol,
          price: (data['price'] as num).toDouble(),
          change24h: (data['change_24h'] as num?)?.toDouble() ?? 0.0,
          changePercent24h: (data['change_percent_24h'] as num?)?.toDouble() ?? 0.0,
          volume24h: (data['volume_24h'] as num?)?.toDouble() ?? 0.0,
          marketCap: (data['market_cap'] as num?)?.toDouble(),
          high24h: (data['high_24h'] as num?)?.toDouble() ?? 0.0,
          low24h: (data['low_24h'] as num?)?.toDouble() ?? 0.0,
          lastUpdated: DateTime.parse(data['last_updated'] ?? DateTime.now().toIso8601String()),
        );
      } else {
        throw Exception('Failed to load market data: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching market data: $e');
    }
  }

  // Generate trading prediction for a symbol
  Future<TradingSignal> generatePrediction({
    required String symbol,
    String timeframe = '1h',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/predictions/generate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'symbol': symbol,
          'timeframe': timeframe,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return TradingSignal(
          symbol: data['symbol'] ?? symbol,
          signal: _parseSignal(data['signal']),
          confidence: (data['confidence'] as num).toDouble(),
          entryPrice: (data['entry_price'] as num?)?.toDouble() ?? 0.0,
          targetPrice: (data['target_price'] as num?)?.toDouble() ?? 0.0,
          stopLoss: (data['stop_loss'] as num?)?.toDouble() ?? 0.0,
          reasoning: (data['reasoning'] as List?)?.cast<String>() ?? [],
          timestamp: DateTime.parse(data['timestamp'] ?? DateTime.now().toIso8601String()),
          recommendation: data['recommendation'] ?? 'No recommendation available',
        );
      } else {
        throw Exception('Failed to generate prediction: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error generating prediction: $e');
    }
  }

  // Get asset categories
  Future<List<Map<String, dynamic>>> getAssetCategories() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/assets/categories'));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return (data['categories'] as List).cast<Map<String, dynamic>>();
      } else {
        throw Exception('Failed to load categories: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching categories: $e');
    }
  }

  // Health check
  Future<bool> healthCheck() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // Helper method to parse category from string
  AssetCategory _parseCategory(String categoryString) {
    switch (categoryString.toLowerCase()) {
      case 'crypto':
      case 'cryptocurrency':
        return AssetCategory.crypto;
      case 'forex':
        return AssetCategory.forex;
      case 'stocks':
        return AssetCategory.stocks;
      case 'commodities':
        return AssetCategory.commodities;
      case 'indices':
        return AssetCategory.indices;
      default:
        return AssetCategory.stocks;
    }
  }

  // Helper method to parse signal from string
  SignalType _parseSignal(String signalString) {
    switch (signalString.toLowerCase()) {
      case 'buy':
        return SignalType.buy;
      case 'sell':
        return SignalType.sell;
      case 'hold':
      default:
        return SignalType.hold;
    }
  }
}