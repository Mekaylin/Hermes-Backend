import 'package:flutter/material.dart';

// Asset Categories
enum AssetCategory { crypto, forex, stocks, commodities, indices }

// Trading Signal Types
enum SignalType { buy, hold, sell }

// Asset Model
class Asset {
  final String symbol;
  final String name;
  final AssetCategory category;
  final String exchange;
  final String description;

  const Asset({
    required this.symbol,
    required this.name,
    required this.category,
    required this.exchange,
    required this.description,
  });

  factory Asset.fromJson(Map<String, dynamic> json) {
    return Asset(
      symbol: json['symbol'] as String,
      name: json['name'] as String,
      category: AssetCategory.values.firstWhere(
        (e) => e.name == json['category'],
        orElse: () => AssetCategory.stocks,
      ),
      exchange: json['exchange'] as String,
      description: json['description'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'symbol': symbol,
      'name': name,
      'category': category.name,
      'exchange': exchange,
      'description': description,
    };
  }
}

// Market Data Model
class MarketData {
  final String symbol;
  final double price;
  final double change24h;
  final double changePercent24h;
  final double volume24h;
  final double? marketCap;
  final double high24h;
  final double low24h;
  final DateTime lastUpdated;

  const MarketData({
    required this.symbol,
    required this.price,
    required this.change24h,
    required this.changePercent24h,
    required this.volume24h,
    this.marketCap,
    required this.high24h,
    required this.low24h,
    required this.lastUpdated,
  });

  factory MarketData.fromJson(Map<String, dynamic> json) {
    return MarketData(
      symbol: json['symbol'] as String,
      price: (json['price'] as num).toDouble(),
      change24h: (json['change_24h'] as num).toDouble(),
      changePercent24h: (json['change_percent_24h'] as num).toDouble(),
      volume24h: (json['volume_24h'] as num).toDouble(),
      marketCap: json['market_cap'] != null 
          ? (json['market_cap'] as num).toDouble() 
          : null,
      high24h: (json['high_24h'] as num).toDouble(),
      low24h: (json['low_24h'] as num).toDouble(),
      lastUpdated: DateTime.parse(json['last_updated'] as String),
    );
  }

  bool get isPositive => changePercent24h >= 0;

  // Add aliases for compatibility with widgets
  double get change => change24h;
  double get changePercent => changePercent24h;
  double get volume => volume24h;
  double get high => high24h;
  double get low => low24h;
  DateTime get timestamp => lastUpdated;
}

// Trading Signal Model
class TradingSignal {
  final String symbol;
  final SignalType signal;
  final double confidence;
  final double entryPrice;
  final double targetPrice;
  final double stopLoss;
  final List<String> reasoning;
  final DateTime timestamp;
  final String recommendation;

  const TradingSignal({
    required this.symbol,
    required this.signal,
    required this.confidence,
    required this.entryPrice,
    required this.targetPrice,
    required this.stopLoss,
    required this.reasoning,
    required this.timestamp,
    required this.recommendation,
  });

  factory TradingSignal.fromJson(Map<String, dynamic> json) {
    return TradingSignal(
      symbol: json['symbol'] as String,
      signal: SignalType.values.firstWhere(
        (e) => e.name.toLowerCase() == (json['signal'] as String).toLowerCase(),
        orElse: () => SignalType.hold,
      ),
      confidence: (json['confidence'] as num).toDouble(),
      entryPrice: (json['entry_price'] as num).toDouble(),
      targetPrice: (json['target_price'] as num).toDouble(),
      stopLoss: (json['stop_loss'] as num).toDouble(),
      reasoning: (json['reasoning'] as List).cast<String>(),
      timestamp: DateTime.parse(json['timestamp'] as String),
      recommendation: json['recommendation'] as String,
    );
  }

  Color get signalColor {
    switch (signal) {
      case SignalType.buy:
        return const Color(0xFF10B981); // Green
      case SignalType.sell:
        return const Color(0xFFEF4444); // Red
      case SignalType.hold:
        return const Color(0xFFF59E0B); // Amber
    }
  }

  String get signalText {
    switch (signal) {
      case SignalType.buy:
        return 'BUY';
      case SignalType.sell:
        return 'SELL';
      case SignalType.hold:
        return 'HOLD';
    }
  }

  String get confidenceLevel {
    if (confidence > 75) return 'High';
    if (confidence > 50) return 'Medium';
    return 'Low';
  }

  // Add explanation alias for compatibility with widgets
  String get explanation => reasoning.isNotEmpty ? reasoning.join('. ') : recommendation;
}
