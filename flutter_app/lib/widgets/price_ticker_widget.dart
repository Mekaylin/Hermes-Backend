import 'package:flutter/material.dart';

class PriceTickerWidget extends StatelessWidget {
  final double currentPrice;
  final double priceChange;
  final double priceChangePercent;

  const PriceTickerWidget({
    super.key,
    required this.currentPrice,
    required this.priceChange,
    required this.priceChangePercent,
  });

  @override
  Widget build(BuildContext context) {
    final isPositive = priceChange >= 0;
    final changeColor = isPositive ? Colors.green.shade400 : Colors.red.shade400;
    final changeIcon = isPositive ? Icons.trending_up : Icons.trending_down;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0E1A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '\$${currentPrice.toStringAsFixed(2)}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(
                    changeIcon,
                    color: changeColor,
                    size: 16,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${isPositive ? '+' : ''}\$${priceChange.toStringAsFixed(2)}',
                    style: TextStyle(
                      color: changeColor,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: changeColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${isPositive ? '+' : ''}${priceChangePercent.toStringAsFixed(2)}%',
                      style: TextStyle(
                        color: changeColor,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.blue.shade900.withOpacity(0.3),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.currency_bitcoin,
              color: Colors.blue.shade400,
              size: 24,
            ),
          ),
        ],
      ),
    );
  }
}
