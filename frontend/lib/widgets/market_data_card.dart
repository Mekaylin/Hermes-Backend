import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/trading_data.dart';

class MarketDataCard extends StatelessWidget {
  final MarketData marketData;
  final String symbol;

  const MarketDataCard({
    super.key,
    required this.marketData,
    required this.symbol,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isPositive = marketData.change >= 0;
    
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with symbol and price
            Row(
              children: [
                // Symbol icon
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      symbol.length > 3 
                          ? symbol.substring(0, 3).toUpperCase()
                          : symbol.toUpperCase(),
                      style: TextStyle(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                
                // Price and change
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        symbol.toUpperCase(),
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Text(
                            '\$${marketData.price.toStringAsFixed(2)}',
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: isPositive ? Colors.green : Colors.red,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  isPositive ? Icons.arrow_upward : Icons.arrow_downward,
                                  color: Colors.white,
                                  size: 16,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  '${isPositive ? '+' : ''}${marketData.changePercent.toStringAsFixed(2)}%',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                // Last updated
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Icon(
                      Icons.access_time,
                      size: 16,
                      color: theme.colorScheme.onSurface.withOpacity(0.6),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _formatTimestamp(marketData.timestamp),
                      style: TextStyle(
                        fontSize: 12,
                        color: theme.colorScheme.onSurface.withOpacity(0.6),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // Market stats
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Volume',
                    _formatVolume(marketData.volume),
                    Icons.bar_chart,
                    theme,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'High',
                    '\$${marketData.high.toStringAsFixed(2)}',
                    Icons.keyboard_arrow_up,
                    theme,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Low',
                    '\$${marketData.low.toStringAsFixed(2)}',
                    Icons.keyboard_arrow_down,
                    theme,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 20),
            
            // Mini price chart
            SizedBox(
              height: 100,
              child: _buildMiniChart(theme),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.outline.withOpacity(0.2),
        ),
      ),
      child: Column(
        children: [
          Icon(
            icon,
            size: 20,
            color: theme.colorScheme.primary,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: theme.colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMiniChart(ThemeData theme) {
    // Generate sample price data points for demonstration
    final spots = <FlSpot>[];
    final currentPrice = marketData.price;
    final range = currentPrice * 0.05; // 5% range
    
    for (int i = 0; i < 24; i++) {
      final variation = (i % 3 == 0 ? 1 : -1) * (range * (i % 4) / 4);
      spots.add(FlSpot(i.toDouble(), currentPrice + variation));
    }

    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: const FlTitlesData(show: false),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: marketData.change >= 0 ? Colors.green : Colors.red,
            barWidth: 2,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              color: (marketData.change >= 0 ? Colors.green : Colors.red).withOpacity(0.1),
            ),
          ),
        ],
        minX: 0,
        maxX: 23,
        minY: spots.map((e) => e.y).reduce((a, b) => a < b ? a : b) * 0.999,
        maxY: spots.map((e) => e.y).reduce((a, b) => a > b ? a : b) * 1.001,
      ),
    );
  }

  String _formatVolume(double volume) {
    if (volume >= 1000000000) {
      return '${(volume / 1000000000).toStringAsFixed(1)}B';
    } else if (volume >= 1000000) {
      return '${(volume / 1000000).toStringAsFixed(1)}M';
    } else if (volume >= 1000) {
      return '${(volume / 1000).toStringAsFixed(1)}K';
    } else {
      return volume.toStringAsFixed(0);
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inSeconds < 60) {
      return 'Live';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inDays}d ago';
    }
  }
}
