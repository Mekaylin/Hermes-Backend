import 'package:flutter/material.dart';

class TopRecommendationWidget extends StatelessWidget {
  final Map<String, dynamic> recommendation;
  final bool isPaperMode;
  final VoidCallback onPaperTrade;
  final VoidCallback onViewDetails;

  const TopRecommendationWidget({
    super.key,
    required this.recommendation,
    required this.isPaperMode,
    required this.onPaperTrade,
    required this.onViewDetails,
  });

  Color _getRecommendationColor(String rec) {
    if (rec.toLowerCase().contains('buy')) return Colors.green.shade400;
    if (rec.toLowerCase().contains('sell')) return Colors.red.shade400;
    return Colors.yellow.shade600;
  }

  IconData _getRecommendationIcon(String rec) {
    if (rec.toLowerCase().contains('buy')) return Icons.trending_up;
    if (rec.toLowerCase().contains('sell')) return Icons.trending_down;
    return Icons.remove;
  }

  @override
  Widget build(BuildContext context) {
    final topRec = recommendation['top_recommendation'];
    final confidencePct = recommendation['confidence_pct'] ?? 0;
    final expectedReturnPct = recommendation['expected_return_pct'] ?? '0.0%';
    final riskLevel = recommendation['risk_level'] ?? 'Medium';
    final reasons = List<String>.from(recommendation['reasons'] ?? []);
    final targetPrice = recommendation['target_price'] ?? 0.0;
    final stopLoss = recommendation['stop_loss'] ?? 0.0;
    final positionSizePct = recommendation['position_size_pct'] ?? 1.0;
    
    final recColor = _getRecommendationColor(topRec['recommendation']);
    final symbol = topRec['symbol'];
    final currentPrice = topRec['current_price'];

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            recColor.withOpacity(0.15),
            recColor.withOpacity(0.05),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: recColor.withOpacity(0.3), width: 2),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: recColor.withOpacity(0.2),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.psychology,
                        color: recColor,
                        size: 28,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Top Recommendation',
                            style: TextStyle(
                              color: Colors.grey.shade400,
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Text(
                                symbol,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                '\$${currentPrice.toStringAsFixed(2)}',
                                style: TextStyle(
                                  color: Colors.grey.shade300,
                                  fontSize: 16,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: recColor.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        '$confidencePct% CONFIDENCE',
                        style: TextStyle(
                          color: recColor,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 20),
                
                // Main Recommendation
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      _getRecommendationIcon(topRec['recommendation']),
                      color: recColor,
                      size: 32,
                    ),
                    const SizedBox(width: 12),
                    Text(
                      topRec['recommendation'].toString().toUpperCase(),
                      style: TextStyle(
                        fontSize: 36,
                        color: recColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 8),
                
                Text(
                  'Expected: $expectedReturnPct in next 24h',
                  style: TextStyle(
                    color: Colors.grey.shade300,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
          
          // Why Section
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0A0E1A),
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(18),
                bottomRight: Radius.circular(18),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.lightbulb_outline, color: Colors.blue.shade400, size: 20),
                    const SizedBox(width: 8),
                    const Text(
                      'Why this?',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                
                // Reasons
                ...reasons.map((reason) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '•',
                        style: TextStyle(color: recColor, fontSize: 16),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          reason,
                          style: TextStyle(
                            color: Colors.grey.shade300,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ],
                  ),
                )),
                
                const SizedBox(height: 16),
                
                // Risk & Targets
                Row(
                  children: [
                    Expanded(
                      child: _buildInfoCard(
                        'Risk Level',
                        riskLevel,
                        _getRiskColor(riskLevel),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildInfoCard(
                        'Target',
                        '\$${targetPrice.toStringAsFixed(2)}',
                        Colors.green.shade400,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildInfoCard(
                        'Stop Loss',
                        '\$${stopLoss.toStringAsFixed(2)}',
                        Colors.red.shade400,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 16),
                
                // Action Buttons
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: onViewDetails,
                        icon: const Icon(Icons.visibility),
                        label: const Text('View Details'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue.shade600,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton.icon(
                      onPressed: onPaperTrade,
                      icon: const Icon(Icons.school),
                      label: const Text('Paper Trade'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green.shade600,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 12),
                
                // Position Size Suggestion
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1F2E),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFF2A2F3E)),
                  ),
                  child: Text(
                    'Suggested position size: ${positionSizePct.toStringAsFixed(1)}% of portfolio',
                    style: TextStyle(
                      color: Colors.grey.shade400,
                      fontSize: 12,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _getRiskColor(String risk) {
    switch (risk.toLowerCase()) {
      case 'low':
        return Colors.green.shade400;
      case 'high':
        return Colors.red.shade400;
      default:
        return Colors.yellow.shade600;
    }
  }

  Widget _buildInfoCard(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 10,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
