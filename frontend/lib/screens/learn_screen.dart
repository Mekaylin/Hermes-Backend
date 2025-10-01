import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/trading_data_provider.dart';

class LearnScreen extends StatelessWidget {
  const LearnScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // App Header
            SliverAppBar(
              expandedHeight: 120,
              floating: true,
              pinned: true,
              backgroundColor: const Color(0xFF0A0E1A),
              flexibleSpace: FlexibleSpaceBar(
                title: const Text(
                  'Learn Trading',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                centerTitle: false,
                titlePadding: const EdgeInsets.only(left: 20, bottom: 16),
                background: Container(
                  padding: const EdgeInsets.only(left: 20, bottom: 40),
                  alignment: Alignment.bottomLeft,
                  child: Text(
                    'Master trading concepts and strategies',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(0.7),
                    ),
                  ),
                ),
              ),
            ),

            // Content
            SliverPadding(
              padding: const EdgeInsets.all(20),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  // Quick Start Guide
                  _buildQuickStartSection(),
                  const SizedBox(height: 24),

                  // Trading Basics
                  _buildTradingBasicsSection(),
                  const SizedBox(height: 24),

                  // Market Types
                  _buildMarketTypesSection(),
                  const SizedBox(height: 24),

                  // AI Signals Guide
                  _buildAISignalsSection(),
                  const SizedBox(height: 24),

                  // Risk Management
                  _buildRiskManagementSection(),
                  
                  const SizedBox(height: 100), // Bottom padding
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickStartSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1A1F2E), Color(0xFF2A2F3E)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.rocket_launch,
                  color: Colors.green,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              const Expanded(
                child: Text(
                  'Quick Start Guide',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildLearningStep(
            '1',
            'Choose Your Market',
            'Start with Forex (currencies) or Crypto for beginners. They\'re liquid and have plenty of educational resources.',
            Icons.language,
          ),
          const SizedBox(height: 16),
          
          _buildLearningStep(
            '2',
            'Analyze with AI',
            'Use our AI assistant to get trading signals. Look for high confidence scores (70%+) and understand the reasoning.',
            Icons.psychology,
          ),
          const SizedBox(height: 16),
          
          _buildLearningStep(
            '3',
            'Start Small',
            'Always use proper risk management. Never risk more than 1-2% of your capital on a single trade.',
            Icons.shield_outlined,
          ),
          const SizedBox(height: 16),
          
          _buildLearningStep(
            '4',
            'Learn Continuously',
            'Review your decisions, study market patterns, and keep improving your trading knowledge.',
            Icons.trending_up,
          ),
        ],
      ),
    );
  }

  Widget _buildLearningStep(String number, String title, String description, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0E1A).withOpacity(0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Center(
              child: Text(
                number,
                style: const TextStyle(
                  color: Colors.blue,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(icon, color: Colors.white, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.7),
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTradingBasicsSection() {
    return _buildLearningCard(
      'Trading Basics',
      Icons.school,
      Colors.orange,
      [
        _buildTopicTile(
          'What is Trading?',
          'Learn the fundamentals of buying and selling financial instruments',
          Icons.info_outline,
        ),
        _buildTopicTile(
          'Market Orders vs Limit Orders',
          'Understand different order types and when to use them',
          Icons.assignment,
        ),
        _buildTopicTile(
          'Bull vs Bear Markets',
          'Recognize market trends and how they affect trading strategies',
          Icons.trending_up,
        ),
        _buildTopicTile(
          'Support and Resistance',
          'Identify key price levels that influence market movement',
          Icons.show_chart,
        ),
      ],
    );
  }

  Widget _buildMarketTypesSection() {
    return _buildLearningCard(
      'Market Types',
      Icons.public,
      Colors.purple,
      [
        _buildTopicTile(
          'Forex (Currencies)',
          'Trade currency pairs like EUR/USD, GBP/JPY - Most liquid market',
          Icons.currency_exchange,
        ),
        _buildTopicTile(
          'Cryptocurrencies',
          'Digital assets like Bitcoin, Ethereum - 24/7 trading available',
          Icons.currency_bitcoin,
        ),
        _buildTopicTile(
          'Stocks & Indices',
          'Company shares and market indices - Traditional investment options',
          Icons.business,
        ),
        _buildTopicTile(
          'Commodities',
          'Physical goods like Gold, Oil, Silver - Hedge against inflation',
          Icons.grain,
        ),
      ],
    );
  }

  Widget _buildAISignalsSection() {
    return _buildLearningCard(
      'Understanding AI Signals',
      Icons.psychology,
      Colors.blue,
      [
        _buildTopicTile(
          'Signal Types',
          'BUY, SELL, HOLD - What each recommendation means for your trading',
          Icons.signal_cellular_alt,
        ),
        _buildTopicTile(
          'Confidence Scores',
          'How to interpret confidence levels and use them in decision making',
          Icons.percent,
        ),
        _buildTopicTile(
          'Market Analysis',
          'Technical indicators and market sentiment behind AI recommendations',
          Icons.analytics,
        ),
        _buildTopicTile(
          'Risk Assessment',
          'Understanding volatility scores and risk factors in signals',
          Icons.warning_amber,
        ),
      ],
    );
  }

  Widget _buildRiskManagementSection() {
    return _buildLearningCard(
      'Risk Management',
      Icons.shield,
      Colors.red,
      [
        _buildTopicTile(
          'Position Sizing',
          'How much to invest per trade - Never risk more than you can afford',
          Icons.pie_chart,
        ),
        _buildTopicTile(
          'Stop Losses',
          'Protect your capital by setting automatic exit points',
          Icons.stop_circle,
        ),
        _buildTopicTile(
          'Diversification',
          'Spread risk across different assets and market sectors',
          Icons.scatter_plot,
        ),
        _buildTopicTile(
          'Emotional Trading',
          'Control fear and greed - Stick to your trading plan',
          Icons.psychology_alt,
        ),
      ],
    );
  }

  Widget _buildLearningCard(String title, IconData icon, Color accentColor, List<Widget> children) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: accentColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  color: accentColor,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ...children,
        ],
      ),
    );
  }

  Widget _buildTopicTile(String title, String description, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0E1A).withOpacity(0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
        ),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: Colors.white.withOpacity(0.7),
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withOpacity(0.6),
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
          Icon(
            Icons.arrow_forward_ios,
            color: Colors.white.withOpacity(0.3),
            size: 16,
          ),
        ],
      ),
    );
  }
}
