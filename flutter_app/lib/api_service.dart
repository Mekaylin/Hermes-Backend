import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://localhost:8001';

  static Future<Map<String, dynamic>> fetchTopRecommendation(String riskPreference) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/top-recommendation?risk_preference=$riskPreference'),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load recommendation: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<List<dynamic>> fetchRecommendations(String riskPreference, int limit) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/scout?risk_preference=$riskPreference&limit=$limit'),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load recommendations: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<Map<String, dynamic>> fetchSignal(String asset) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/signal?asset=$asset'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {'signal': 'hold', 'confidence': 0.5, 'predicted_change': 0.0};
      }
    } catch (e) {
      return {'signal': 'hold', 'confidence': 0.5, 'predicted_change': 0.0};
    }
  }

  static Future<List<dynamic>> fetchHistory(String asset) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/history?asset=$asset'));
      if (response.statusCode == 200) {
        return json.decode(response.body)['history'];
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  static Future<List<dynamic>> fetchNews(String asset) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/news?asset=$asset'));
      if (response.statusCode == 200) {
        return json.decode(response.body)['news'];
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  static Future<Map<String, dynamic>> healthCheck() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {'status': 'error'};
      }
    } catch (e) {
      return {'status': 'offline'};
    }
  }
}
