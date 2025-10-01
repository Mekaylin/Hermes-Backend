import 'package:flutter/material.dart';

class AISignalWidget extends StatelessWidget {
  final String signal;
  final double confidence;
  final double targetPrice;
  final double currentPrice;

  const AISignalWidget({
    super.key,
    required this.signal,
    required this.confidence,
    required this.targetPrice,
    required this.currentPrice,
  });

  Color getSignalColor() {
    switch (signal.toLowerCase()) {
      case 'buy':
        return Colors.green.shade400;
      case 'sell':
        return Colors.red.shade400;
      default:
        return Colors.yellow.shade600;
    }
  }

  IconData getSignalIcon() {
    switch (signal.toLowerCase()) {
      case 'buy':
        return Icons.trending_up;
      case 'sell':
        return Icons.trending_down;
      default:
        return Icons.remove;
    }
  }

  String getSignalDescription() {
    switch (signal.toLowerCase()) {
      case 'buy':
        return 'AI recommends buying this asset';
      case 'sell':
        return 'AI recommends selling this asset';
      default:
        return 'AI recommends holding position';
    }
  }

  @override
  Widget build(BuildContext context) {
    final signalColor = getSignalColor();
    final potentialGain = targetPrice - currentPrice;
    final potentialGainPercent = currentPrice > 0 ? (potentialGain / currentPrice) * 100 : 0;

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            signalColor.withOpacity(0.1),
            signalColor.withOpacity(0.05),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: signalColor.withOpacity(0.3), width: 2),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: signalColor.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.psychology,
                  color: signalColor,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI Trade Signal',
                      style: TextStyle(
                        color: Colors.grey.shade400,
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          getSignalIcon(),
                          color: signalColor,
                          size: 24,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          signal.toUpperCase(),
                          style: TextStyle(
                            fontSize: 32,
                            color: signalColor,
                            fontWeight: FontWeight.bold,
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
                  color: signalColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${(confidence * 100).toStringAsFixed(0)}% CONFIDENCE',
                  style: TextStyle(
                    color: signalColor,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Confidence meter
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Confidence Level',
                    style: TextStyle(
                      color: Colors.grey.shade400,
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    '${(confidence * 100).toStringAsFixed(1)}%',
                    style: TextStyle(
                      color: signalColor,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              LinearProgressIndicator(
                value: confidence,
                backgroundColor: Colors.grey.shade800,
                valueColor: AlwaysStoppedAnimation<Color>(signalColor),
                minHeight: 6,
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Target and potential gain
          Row(
            children: [
              Expanded(
                child: _buildInfoCard(
                  'Target Price',
                  '\$${targetPrice.toStringAsFixed(2)}',
                  Colors.blue.shade400,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildInfoCard(
                  'Potential ${potentialGain >= 0 ? 'Gain' : 'Loss'}',
                  '${potentialGain >= 0 ? '+' : ''}${potentialGainPercent.toStringAsFixed(1)}%',
                  potentialGain >= 0 ? Colors.green.shade400 : Colors.red.shade400,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Description
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF0A0E1A),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFF2A2F3E)),
            ),
            child: Text(
              getSignalDescription(),
              style: TextStyle(
                color: Colors.grey.shade300,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0E1A),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
