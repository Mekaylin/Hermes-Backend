import 'package:flutter/material.dart';

class RiskSelectorWidget extends StatelessWidget {
  final String selectedRisk;
  final Function(String) onRiskChanged;

  const RiskSelectorWidget({
    super.key,
    required this.selectedRisk,
    required this.onRiskChanged,
  });

  @override
  Widget build(BuildContext context) {
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
              Icon(Icons.shield_outlined, color: Colors.blue.shade400, size: 24),
              const SizedBox(width: 12),
              const Text(
                'Risk Preference',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: () => _showRiskExplanationDialog(context),
                icon: Icon(Icons.help_outline, color: Colors.grey.shade400),
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          Text(
            'Choose your comfort level for trading decisions',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 14,
            ),
          ),
          
          const SizedBox(height: 20),
          
          Row(
            children: [
              Expanded(
                child: _buildRiskOption(
                  'Conservative',
                  'Low',
                  Icons.security,
                  Colors.green.shade400,
                  'Safe, steady gains',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildRiskOption(
                  'Balanced',
                  'Medium',
                  Icons.balance,
                  Colors.yellow.shade600,
                  'Moderate risk/reward',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildRiskOption(
                  'Growth',
                  'High',
                  Icons.trending_up,
                  Colors.red.shade400,
                  'Higher potential gains',
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF1A1F2E),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: Colors.blue.shade400, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _getRiskDescription(selectedRisk),
                    style: TextStyle(
                      color: Colors.grey.shade300,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRiskOption(String title, String value, IconData icon, Color color, String subtitle) {
    final isSelected = selectedRisk == value;
    
    return GestureDetector(
      onTap: () => onRiskChanged(value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.15) : const Color(0xFF1A1F2E),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? color : const Color(0xFF2A2F3E),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: isSelected ? color : Colors.grey.shade400,
              size: 24,
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.grey.shade400,
                fontSize: 14,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(
                color: Colors.grey.shade500,
                fontSize: 10,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  String _getRiskDescription(String risk) {
    switch (risk) {
      case 'Low':
        return 'Conservative approach with lower volatility stocks and smaller position sizes. Focus on dividend stocks and blue chips.';
      case 'High':
        return 'Growth-oriented approach with higher volatility stocks and larger position sizes. Includes growth stocks and emerging markets.';
      default:
        return 'Balanced approach mixing stable and growth stocks with moderate position sizes. Good for most investors.';
    }
  }

  void _showRiskExplanationDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF0F1420),
        title: Row(
          children: [
            Icon(Icons.shield_outlined, color: Colors.blue.shade400),
            const SizedBox(width: 12),
            const Text(
              'Risk Levels Explained',
              style: TextStyle(color: Colors.white),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildRiskExplanation(
              'Conservative (Low Risk)',
              Colors.green.shade400,
              [
                'Focus on stable, dividend-paying stocks',
                'Smaller position sizes (1-3% per trade)',
                'Lower volatility, steadier returns',
                'Better for capital preservation',
              ],
            ),
            const SizedBox(height: 16),
            _buildRiskExplanation(
              'Balanced (Medium Risk)',
              Colors.yellow.shade600,
              [
                'Mix of stable and growth stocks',
                'Moderate position sizes (3-5% per trade)',
                'Balanced risk/reward ratio',
                'Good for most investors',
              ],
            ),
            const SizedBox(height: 16),
            _buildRiskExplanation(
              'Growth (High Risk)',
              Colors.red.shade400,
              [
                'Focus on high-growth potential stocks',
                'Larger position sizes (5-10% per trade)',
                'Higher volatility, bigger swings',
                'Better for capital growth',
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Got it',
              style: TextStyle(color: Colors.blue.shade400),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRiskExplanation(String title, Color color, List<String> points) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            color: color,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        ...points.map((point) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 2),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('•', style: TextStyle(color: color)),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  point,
                  style: TextStyle(
                    color: Colors.grey.shade300,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
        )),
      ],
    );
  }
}
