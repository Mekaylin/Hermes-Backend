import 'package:flutter/material.dart';

class LearnHelpWidget extends StatelessWidget {
  const LearnHelpWidget({super.key});

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
              Icon(Icons.school, color: Colors.purple.shade400, size: 24),
              const SizedBox(width: 12),
              const Text(
                'Learn & Help',
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
            'Quick guides and explanations to help you understand trading',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 14,
            ),
          ),
          
          const SizedBox(height: 20),
          
          Row(
            children: [
              Expanded(
                child: _buildHelpCard(
                  context,
                  'What is Confidence?',
                  Icons.psychology,
                  Colors.blue.shade400,
                  _getConfidenceExplanation(),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildHelpCard(
                  context,
                  'Risk Levels',
                  Icons.shield,
                  Colors.green.shade400,
                  _getRiskExplanation(),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          Row(
            children: [
              Expanded(
                child: _buildHelpCard(
                  context,
                  'Paper Trading',
                  Icons.school,
                  Colors.orange.shade400,
                  _getPaperTradingExplanation(),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildHelpCard(
                  context,
                  'Market Signals',
                  Icons.trending_up,
                  Colors.purple.shade400,
                  _getSignalsExplanation(),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.purple.shade400.withOpacity(0.1),
                  Colors.blue.shade400.withOpacity(0.1),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.purple.shade400.withOpacity(0.3)),
            ),
            child: Column(
              children: [
                Icon(Icons.lightbulb, color: Colors.yellow.shade400, size: 28),
                const SizedBox(height: 12),
                const Text(
                  'Quick Tips for Beginners',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                ..._getQuickTips().map((tip) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '💡',
                        style: TextStyle(fontSize: 16),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          tip,
                          style: TextStyle(
                            color: Colors.grey.shade300,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                )),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHelpCard(BuildContext context, String title, IconData icon, Color color, String content) {
    return GestureDetector(
      onTap: () => _showHelpDialog(context, title, content, color),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF1A1F2E),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF2A2F3E)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Tap to learn',
              style: TextStyle(
                color: Colors.grey.shade500,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showHelpDialog(BuildContext context, String title, String content, Color color) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF0F1420),
        title: Row(
          children: [
            Icon(Icons.help_outline, color: color),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        content: Text(
          content,
          style: TextStyle(
            color: Colors.grey.shade300,
            fontSize: 14,
            height: 1.5,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Got it!',
              style: TextStyle(color: color),
            ),
          ),
        ],
      ),
    );
  }

  String _getConfidenceExplanation() {
    return '''The confidence percentage shows how sure our AI is about a recommendation.

🎯 90-100%: Very confident - Strong signals from multiple indicators
🎯 70-89%: Confident - Good signals, worth considering
🎯 50-69%: Moderate - Mixed signals, be cautious
🎯 Below 50%: Low confidence - Wait for better opportunities

Higher confidence doesn't guarantee success, but it means our AI sees stronger patterns supporting the recommendation.''';
  }

  String _getRiskExplanation() {
    return '''Risk levels help you choose investments that match your comfort:

🛡️ LOW RISK (Conservative):
• Stable, established companies
• Smaller position sizes
• Lower volatility
• Good for preserving money

⚖️ MEDIUM RISK (Balanced):
• Mix of stable and growth stocks
• Moderate position sizes
• Balanced approach
• Good for most people

🚀 HIGH RISK (Growth):
• High-growth potential stocks
• Larger position sizes
• More volatile
• Good for growing money faster''';
  }

  String _getPaperTradingExplanation() {
    return '''Paper trading lets you practice without real money!

📝 What it is:
• Virtual trading with fake money
• Learn without financial risk
• Track your performance
• Build confidence

🎯 Benefits:
• Practice strategies safely
• Learn from mistakes
• Test AI recommendations
• Build trading skills

💡 Perfect for beginners who want to learn before investing real money. All your trades are simulated but use real market prices!''';
  }

  String _getSignalsExplanation() {
    return '''Market signals are clues about where prices might go:

📈 BUY Signal:
• Price likely to go up
• Good time to enter position
• Positive market indicators

📉 SELL Signal:
• Price likely to go down
• Good time to exit position
• Negative market indicators

➡️ HOLD Signal:
• Wait and see
• Mixed or unclear signals
• Consider other opportunities

Our AI analyzes multiple factors including price patterns, news sentiment, and market trends to generate these signals.''';
  }

  List<String> _getQuickTips() {
    return [
      'Start with paper trading to practice without risk',
      'Never invest more than you can afford to lose',
      'Higher confidence signals are generally more reliable',
      'Conservative risk settings are better for beginners',
      'Always do your own research before making trades',
      'Diversify - don\'t put all money in one stock',
    ];
  }
}
