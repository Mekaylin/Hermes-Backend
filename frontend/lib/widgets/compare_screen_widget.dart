import 'package:flutter/material.dart';

class CompareScreenWidget extends StatelessWidget {
  final Map<String, dynamic> recommendations;

  const CompareScreenWidget({
    super.key,
    required this.recommendations,
  });

  @override
  Widget build(BuildContext context) {
    final allRecs = recommendations['all_recommendations'] ?? [];
    final topRec = recommendations['top_recommendation'];
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1420),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.compare_arrows, color: Colors.cyan.shade400, size: 24),
              const SizedBox(width: 12),
              const Text(
                'Compare All Options',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          Text(
            'See all AI recommendations ranked by confidence',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 14,
            ),
          ),
          
          const SizedBox(height: 20),
          
          if (allRecs.isEmpty)
            _buildEmptyState()
          else
            Column(
              children: [
                // Top recommendation highlight
                if (topRec != null) ...[
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.amber.withOpacity(0.15),
                          Colors.amber.withOpacity(0.05),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.amber.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.amber.withOpacity(0.2),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(Icons.star, color: Colors.amber, size: 20),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'TOP PICK: ${topRec['symbol']}',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '${recommendations['confidence_pct']}% confidence • ${topRec['recommendation']}',
                                style: TextStyle(
                                  color: Colors.grey.shade300,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Text(
                          '${recommendations['expected_return_pct']}',
                          style: const TextStyle(
                            color: Colors.amber,
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                
                // All recommendations list
                const Text(
                  'All Recommendations',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                
                ...allRecs.asMap().entries.map((entry) {
                  final index = entry.key;
                  final rec = entry.value;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: _buildRecommendationItem(rec, index + 1),
                  );
                }),
              ],
            ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          Icon(
            Icons.search_off,
            size: 64,
            color: Colors.grey.shade600,
          ),
          const SizedBox(height: 16),
          Text(
            'No recommendations available',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Check back later or refresh to get new AI recommendations',
            style: TextStyle(
              color: Colors.grey.shade500,
              fontSize: 12,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationItem(Map<String, dynamic> rec, int rank) {
    final symbol = rec['symbol'] ?? 'N/A';
    final recommendation = rec['recommendation'] ?? 'HOLD';
    final score = rec['score'] ?? 0.0;
    final currentPrice = rec['current_price'] ?? 0.0;
    final expectedReturn = rec['expected_return'] ?? 0.0;
    final confidence = (score * 100).round();
    
    final recColor = _getRecommendationColor(recommendation);
    final isTopThree = rank <= 3;
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isTopThree 
          ? recColor.withOpacity(0.08) 
          : const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isTopThree 
            ? recColor.withOpacity(0.3) 
            : const Color(0xFF2A2F3E),
        ),
      ),
      child: Row(
        children: [
          // Rank
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: isTopThree ? recColor.withOpacity(0.2) : const Color(0xFF2A2F3E),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                '$rank',
                style: TextStyle(
                  color: isTopThree ? recColor : Colors.grey.shade400,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          
          const SizedBox(width: 12),
          
          // Symbol and Price
          Expanded(
            flex: 2,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  symbol,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '\$${currentPrice.toStringAsFixed(2)}',
                  style: TextStyle(
                    color: Colors.grey.shade400,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          
          // Recommendation
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: recColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                recommendation,
                style: TextStyle(
                  color: recColor,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
          
          const SizedBox(width: 8),
          
          // Confidence and Return
          Expanded(
            flex: 2,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '$confidence%',
                  style: TextStyle(
                    color: recColor,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${expectedReturn >= 0 ? '+' : ''}${expectedReturn.toStringAsFixed(1)}%',
                  style: TextStyle(
                    color: Colors.grey.shade400,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _getRecommendationColor(String rec) {
    if (rec.toLowerCase().contains('buy')) return Colors.green.shade400;
    if (rec.toLowerCase().contains('sell')) return Colors.red.shade400;
    return Colors.yellow.shade600;
  }
}
