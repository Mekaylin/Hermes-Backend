import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/trading_data_provider.dart';
import '../widgets/asset_search_widget.dart';
import '../widgets/trading_signal_card.dart';
import '../widgets/market_data_card.dart';
import '../models/trading_data.dart';
import 'portfolio_screen.dart';
import 'learn_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const _MarketScreen(),
    const PortfolioScreen(),
    const LearnScreen(),
    const SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      body: _screens[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF1A1F2E),
          border: Border(
            top: BorderSide(
              color: Colors.white.withOpacity(0.1),
              width: 1,
            ),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          backgroundColor: const Color(0xFF1A1F2E),
          selectedItemColor: Colors.blue,
          unselectedItemColor: Colors.white.withOpacity(0.6),
          selectedLabelStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
          unselectedLabelStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w400,
          ),
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.analytics),
              activeIcon: Icon(Icons.analytics, size: 28),
              label: 'Market',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.account_balance_wallet),
              activeIcon: Icon(Icons.account_balance_wallet, size: 28),
              label: 'Portfolio',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.school),
              activeIcon: Icon(Icons.school, size: 28),
              label: 'Learn',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.settings),
              activeIcon: Icon(Icons.settings, size: 28),
              label: 'Settings',
            ),
          ],
        ),
      ),
    );
  }
}

class _MarketScreen extends StatelessWidget {
  const _MarketScreen();

  @override
  Widget build(BuildContext context) {
    return Consumer<TradingDataProvider>(
      builder: (context, provider, child) {
        return SafeArea(
          child: CustomScrollView(
            slivers: [
              // App Header
              SliverAppBar(
                expandedHeight: 120,
                floating: true,
                pinned: true,
                backgroundColor: const Color(0xFF0A0E1A),
                flexibleSpace: FlexibleSpaceBar(
                  titlePadding: const EdgeInsets.only(left: 20, bottom: 12),
                  centerTitle: false,
                  title: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text(
                        'Hermes AI',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      // subtitle removed per user request
                    ],
                  ),
                ),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.refresh, color: Colors.white),
                    onPressed: provider.isLoading ? null : () {
                      provider.reload();
                    },
                  ),
                  const SizedBox(width: 8),
                ],
              ),

              // Content
              SliverPadding(
                padding: const EdgeInsets.all(20),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    // Asset Search
                    const AssetSearchWidget(),
                    const SizedBox(height: 24),

                    // Error Display
                    if (provider.error != null) ...[
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.red.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: Colors.red.withOpacity(0.3),
                          ),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.error, color: Colors.red),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                provider.error!,
                                style: const TextStyle(color: Colors.red),
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.close, color: Colors.red),
                              onPressed: () => provider.clearError(),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],

                    // Loading Indicator
                    if (provider.isLoading) ...[
                      const Center(
                        child: CircularProgressIndicator(),
                      ),
                      const SizedBox(height: 24),
                    ],

                    // Selected Asset Content
                    if (provider.selectedAsset != null) ...[
                      // Asset Header
                      Container(
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
                                  width: 48,
                                  height: 48,
                                  decoration: BoxDecoration(
                                    color: Colors.blue.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Center(
                                    child: Text(
                                      provider.selectedAsset!.symbol
                                          .substring(0, 2)
                                          .toUpperCase(),
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
                                      Text(
                                        provider.selectedAsset!.symbol,
                                        style: const TextStyle(
                                          fontSize: 20,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.white,
                                        ),
                                      ),
                                      Text(
                                        provider.selectedAsset!.name,
                                        style: TextStyle(
                                          fontSize: 14,
                                          color: Colors.white.withOpacity(0.7),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                ElevatedButton.icon(
                                  onPressed: provider.isLoading ? null : () {
                                    provider.generatePrediction();
                                  },
                                  icon: const Icon(Icons.psychology),
                                  label: const Text('Analyze'),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Market Data
                      if (provider.marketData != null)
                        MarketDataCard(
                          marketData: provider.marketData!,
                          symbol: provider.selectedAsset!.symbol,
                        ),
                      
                      const SizedBox(height: 24),

                      // Trading Signal
                      if (provider.tradingSignal != null)
                        TradingSignalCard(
                          signal: provider.tradingSignal!,
                        ),
                    ] else ...[
                      // Welcome Screen
                      _buildWelcomeScreen(provider),
                    ],

                    const SizedBox(height: 100), // Bottom padding
                  ]),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildWelcomeScreen(TradingDataProvider provider) {
    return Column(
      children: [
        // Welcome Card
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF2196F3), Color(0xFF1976D2)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(
                Icons.trending_up,
                size: 48,
                color: Colors.white,
              ),
              const SizedBox(height: 16),
              const Text(
                'Welcome to Hermes AI',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Your intelligent trading companion powered by advanced AI algorithms.',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.white.withOpacity(0.9),
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: _buildFeatureItem(
                      Icons.analytics,
                      'AI Analysis',
                      'Advanced ML models analyze market patterns',
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildFeatureItem(
                      Icons.security,
                      'Advisory Only',
                      'Safe recommendations without actual trading',
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 32),
        
        // Popular Assets
        if (provider.allAssets.isNotEmpty) ...[
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF1A1F2E),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Popular Assets',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: provider.getPopularAssets().map((asset) {
                    return GestureDetector(
                      onTap: () => provider.setSelectedAsset(asset),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0A0E1A),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: Colors.blue.withOpacity(0.3),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              width: 24,
                              height: 24,
                              decoration: BoxDecoration(
                                color: _getCategoryColor(asset.category),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Center(
                                child: Text(
                                  asset.symbol.substring(0, 1),
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              asset.symbol,
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
        ],
        
        const SizedBox(height: 32),
        
        // Instructions
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0xFF1A1F2E).withOpacity(0.5),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Colors.white.withOpacity(0.1),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'How to Get Started',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 16),
              _buildInstructionStep(
                '1',
                'Search for an asset',
                'Use the search bar above to find stocks, crypto, forex, commodities, or indices',
              ),
              const SizedBox(height: 12),
              _buildInstructionStep(
                '2',
                'View AI analysis',
                'Get real-time market data and AI-powered buy/hold/sell recommendations',
              ),
              const SizedBox(height: 12),
              _buildInstructionStep(
                '3',
                'Make informed decisions',
                'Use our insights as guidance for your trading strategy on other platforms',
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildFeatureItem(IconData icon, String title, String description) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.white, size: 32),
          const SizedBox(height: 8),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            description,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInstructionStep(String number, String title, String description) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 24,
          height: 24,
          decoration: BoxDecoration(
            color: Colors.blue,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Center(
            child: Text(
              number,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                description,
                style: TextStyle(
                  color: Colors.white.withOpacity(0.7),
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Color _getCategoryColor(AssetCategory category) {
    switch (category) {
      case AssetCategory.crypto:
        return Colors.orange;
      case AssetCategory.forex:
        return Colors.green;
      case AssetCategory.stocks:
        return Colors.blue;
      case AssetCategory.commodities:
        return Colors.brown;
      case AssetCategory.indices:
        return Colors.purple;
    }
  }
}
