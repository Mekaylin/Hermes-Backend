import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class MarketChartWidget extends StatelessWidget {
  final List<double> prices;
  final List<double> aiTrend;
  final String selectedAsset;

  const MarketChartWidget({
    super.key, 
    required this.prices, 
    required this.aiTrend,
    required this.selectedAsset,
  });

  @override
  Widget build(BuildContext context) {
    if (prices.isEmpty) {
      return Container(
        height: 300,
        decoration: BoxDecoration(
          color: const Color(0xFF0A0E1A),
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    final minY = prices.reduce((a, b) => a < b ? a : b) * 0.99;
    final maxY = prices.reduce((a, b) => a > b ? a : b) * 1.01;

    return Container(
      height: 300,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0E1A),
        borderRadius: BorderRadius.circular(12),
      ),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: true,
            drawHorizontalLine: true,
            horizontalInterval: (maxY - minY) / 4,
            verticalInterval: 10,
            getDrawingHorizontalLine: (value) {
              return FlLine(
                color: const Color(0xFF2A2F3E),
                strokeWidth: 1,
              );
            },
            getDrawingVerticalLine: (value) {
              return FlLine(
                color: const Color(0xFF2A2F3E),
                strokeWidth: 1,
              );
            },
          ),
          titlesData: FlTitlesData(
            show: true,
            rightTitles: AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            topTitles: AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                interval: 10,
                getTitlesWidget: (value, meta) {
                  return SideTitleWidget(
                    axisSide: meta.axisSide,
                    child: Text(
                      '${value.toInt()}m',
                      style: const TextStyle(
                        color: Colors.grey,
                        fontSize: 10,
                      ),
                    ),
                  );
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: (maxY - minY) / 4,
                reservedSize: 60,
                getTitlesWidget: (value, meta) {
                  return SideTitleWidget(
                    axisSide: meta.axisSide,
                    child: Text(
                      '\$${(value / 1000).toStringAsFixed(0)}K',
                      style: const TextStyle(
                        color: Colors.grey,
                        fontSize: 10,
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
          borderData: FlBorderData(
            show: true,
            border: Border.all(color: const Color(0xFF2A2F3E)),
          ),
          minX: 0,
          maxX: (prices.length - 1).toDouble(),
          minY: minY,
          maxY: maxY,
          lineBarsData: [
            // Price line
            LineChartBarData(
              spots: List.generate(
                prices.length,
                (i) => FlSpot(i.toDouble(), prices[i]),
              ),
              isCurved: true,
              color: Colors.blue.shade400,
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                gradient: LinearGradient(
                  colors: [
                    Colors.blue.shade400.withOpacity(0.3),
                    Colors.blue.shade400.withOpacity(0.0),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
            ),
            // AI Trend line
            if (aiTrend.isNotEmpty)
              LineChartBarData(
                spots: List.generate(
                  aiTrend.length,
                  (i) => FlSpot(i.toDouble(), aiTrend[i]),
                ),
                isCurved: true,
                color: Colors.orange.shade400,
                barWidth: 2,
                isStrokeCapRound: true,
                dotData: FlDotData(show: false),
                dashArray: [5, 5],
              ),
          ],
          lineTouchData: LineTouchData(
            enabled: true,
            touchTooltipData: LineTouchTooltipData(
              tooltipBgColor: const Color(0xFF2A2F3E),
              tooltipRoundedRadius: 8,
              tooltipPadding: const EdgeInsets.all(8),
              getTooltipItems: (List<LineBarSpot> touchedBarSpots) {
                return touchedBarSpots.map((barSpot) {
                  final flSpot = barSpot;
                  final isPrice = barSpot.barIndex == 0;
                  return LineTooltipItem(
                    '${isPrice ? 'Price' : 'AI Trend'}: \$${flSpot.y.toStringAsFixed(2)}',
                    TextStyle(
                      color: isPrice ? Colors.blue.shade400 : Colors.orange.shade400,
                      fontWeight: FontWeight.bold,
                    ),
                  );
                }).toList();
              },
            ),
          ),
        ),
      ),
    );
  }
}
