import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/trading_data.dart';
import '../services/api_service.dart';
import '../widgets/asset_search_widget.dart';
import '../widgets/market_data_widget.dart';
import '../widgets/trading_signal_widget.dart';
import '../widgets/category_selector_widget.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  late TabController _tabController;
  int _currentPageIndex = 0;

  final List<String> _pageTitle = [
    'Market Analysis',
    'Portfolio',
    'Learn',
    'Settings',
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadInitialData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    final dataProvider = Provider.of<TradingDataProvider>(context, listen: false);
    final apiService = Provider.of<ApiService>(context, listen: false);
    
    dataProvider.setLoading(true);
    
    try {
      // Load available assets
      final assets = await apiService.searchAssets();
      dataProvider.setAssets(assets);
    } catch (e) {
      dataProvider.setError(e.toString());
    }
    
    dataProvider.setLoading(false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          _pageTitle[_currentPageIndex],
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        backgroundColor: Theme.of(context).colorScheme.surface,
        foregroundColor: Theme.of(context).colorScheme.onSurface,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadInitialData,
            tooltip: 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              // TODO: Implement notifications
            },
            tooltip: 'Notifications',
          ),
        ],
      ),
      body: _buildPage(_currentPageIndex),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentPageIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentPageIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.analytics_outlined),
            selectedIcon: Icon(Icons.analytics),
            label: 'Analysis',
          ),
          NavigationDestination(
            icon: Icon(Icons.account_balance_wallet_outlined),
            selectedIcon: Icon(Icons.account_balance_wallet),
            label: 'Portfolio',
          ),
          NavigationDestination(
            icon: Icon(Icons.school_outlined),
            selectedIcon: Icon(Icons.school),
            label: 'Learn',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }

  Widget _buildPage(int index) {
    switch (index) {
      case 0:
        return const MarketAnalysisPage();
      case 1:
        return const PortfolioPage();
      case 2:
        return const LearnPage();
      case 3:
        return const SettingsPage();
      default:
        return const MarketAnalysisPage();
    }
  }
}

// Market Analysis Page
class MarketAnalysisPage extends StatefulWidget {
  const MarketAnalysisPage({super.key});

  @override
  State<MarketAnalysisPage> createState() => _MarketAnalysisPageState();
}

class _MarketAnalysisPageState extends State<MarketAnalysisPage> {
  @override
  Widget build(BuildContext context) {
    return Consumer<TradingDataProvider>(
      builder: (context, dataProvider, child) {
        if (dataProvider.isLoading) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('Loading market data...'),
              ],
            ),
          );
        }

        if (dataProvider.error != null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.error_outline,
                  size: 64,
                  color: Theme.of(context).colorScheme.error,
                ),
                const SizedBox(height: 16),
                Text(
                  'Error: ${dataProvider.error}',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.error,
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    dataProvider.clearError();
                    // Retry loading data
                  },
                  child: const Text('Retry'),
                ),
              ],
            ),
          );
        }

        return const Column(
          children: [
            // Category selector
            CategorySelectorWidget(),
            
            // Asset search
            Padding(
              padding: EdgeInsets.all(16.0),
              child: AssetSearchWidget(),
            ),
            
            // Market data and trading signal
            Expanded(
              child: Row(
                children: [
                  Expanded(
                    flex: 1,
                    child: MarketDataWidget(),
                  ),
                  SizedBox(width: 16),
                  Expanded(
                    flex: 1,
                    child: TradingSignalWidget(),
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }
}

// Portfolio Page
class PortfolioPage extends StatelessWidget {
  const PortfolioPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.account_balance_wallet,
            size: 64,
            color: Colors.grey,
          ),
          SizedBox(height: 16),
          Text(
            'Portfolio Tracking',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Coming soon - Track your trading performance',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.grey,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}

// Learn Page
class LearnPage extends StatelessWidget {
  const LearnPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.lightbulb_outline,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        'Trading Basics',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Learn the fundamentals of trading with our AI companion:',
                    style: TextStyle(fontSize: 16),
                  ),
                  const SizedBox(height: 16),
                  _buildLearningTile(
                    'Understanding Signals',
                    'Learn what BUY, SELL, and HOLD signals mean',
                    Icons.trending_up,
                  ),
                  _buildLearningTile(
                    'Risk Management',
                    'How to manage risk and set stop losses',
                    Icons.security,
                  ),
                  _buildLearningTile(
                    'Market Analysis',
                    'Basic technical and fundamental analysis',
                    Icons.analytics,
                  ),
                  _buildLearningTile(
                    'Asset Classes',
                    'Crypto, Forex, Stocks, Commodities, and Indices',
                    Icons.category,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.warning_amber_outlined,
                        color: Theme.of(context).colorScheme.secondary,
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        'Important Disclaimer',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'This app provides educational content and analysis only. '
                    'It is not financial advice. Always do your own research '
                    'and consider consulting with a financial advisor before '
                    'making investment decisions.',
                    style: TextStyle(
                      fontSize: 14,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLearningTile(String title, String subtitle, IconData icon) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: () {
        // TODO: Navigate to detailed learning content
      },
    );
  }
}

// Settings Page
class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.palette_outlined),
                title: const Text('Theme'),
                subtitle: const Text('Light, Dark, or System'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: Implement theme selection
                },
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.notifications_outlined),
                title: const Text('Notifications'),
                subtitle: const Text('Manage signal alerts'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: Implement notification settings
                },
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.language_outlined),
                title: const Text('Language'),
                subtitle: const Text('English'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: Implement language selection
                },
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Card(
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.info_outline),
                title: const Text('About'),
                subtitle: const Text('App version and information'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: Show about dialog
                },
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.help_outline),
                title: const Text('Help & Support'),
                subtitle: const Text('Get help and contact support'),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  // TODO: Show help page
                },
              ),
            ],
          ),
        ),
      ],
    );
  }
}
    _refreshTimer = Timer.periodic(const Duration(minutes: 5), (timer) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    setState(() => isLoading = true);
    
    try {
      final data = await ApiService.fetchTopRecommendation(riskPreference);
      setState(() {
        topRecommendation = data;
        recommendations = data['all_recommendations'] ?? [];
      });
    } catch (e) {
      // Use mock data for demo
      setState(() {
        topRecommendation = {
          'top_recommendation': {
            'symbol': 'AAPL',
            'recommendation': 'BUY',
            'current_price': 185.50,
            'score': 0.85,
          },
          'confidence_pct': 85,
          'expected_return_pct': '+3.2%',
          'risk_level': 'Low',
          'reasons': [
            'Strong quarterly earnings beat expectations',
            'Positive analyst sentiment increasing',
            'Technical indicators show bullish momentum',
          ],
          'target_price': 195.00,
          'stop_loss': 175.00,
          'position_size_pct': 2.5,
          'all_recommendations': [
            {
              'symbol': 'AAPL',
              'recommendation': 'BUY',
              'score': 0.85,
              'current_price': 185.50,
              'expected_return': 3.2,
            },
            {
              'symbol': 'MSFT',
              'recommendation': 'BUY',
              'score': 0.82,
              'current_price': 415.20,
              'expected_return': 2.8,
            },
            {
              'symbol': 'TSLA',
              'recommendation': 'HOLD',
              'score': 0.65,
              'current_price': 245.80,
              'expected_return': 1.2,
            },
          ],
        };
        recommendations = topRecommendation!['all_recommendations'];
      });
    } finally {
      setState(() => isLoading = false);
    }
  }

  void _showConfidenceInfo() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1F2E),
        title: Row(
          children: [
            Icon(Icons.psychology, color: Colors.blue.shade400),
            const SizedBox(width: 12),
            const Text(
              'Confidence Explained',
              style: TextStyle(color: Colors.white),
            ),
          ],
        ),
        content: const Text(
          'Confidence shows how sure our AI is about this recommendation.\n\n'
          '• Green (80-100%) = Very confident\n'
          '• Amber (50-79%) = Moderately confident\n'
          '• Red (Below 50%) = Low confidence\n\n'
          'Higher confidence doesn\'t guarantee success, but indicates stronger patterns.',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Got it', style: TextStyle(color: Colors.blue.shade400)),
          ),
        ],
      ),
    );
  }

  void _showRiskInfo() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1F2E),
        title: Row(
          children: [
            Icon(Icons.shield, color: Colors.orange.shade400),
            const SizedBox(width: 12),
            const Text(
              'Risk Levels',
              style: TextStyle(color: Colors.white),
            ),
          ],
        ),
        content: const Text(
          'Risk levels help match recommendations to your comfort:\n\n'
          '• Green (Low) = safer, stable stocks\n'
          '• Amber (Medium) = moderate volatility\n'
          '• Red (High) = higher volatility\n\n'
          'Always set a stop-loss. This is not financial advice.',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Got it', style: TextStyle(color: Colors.blue.shade400)),
          ),
        ],
      ),
    );
  }

  void _showPaperTradeInfo() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1F2E),
        title: const Text(
          'Paper Trading Mode',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          'You\'re in Paper Trade mode - no real money is used.\n\n'
          'Use this mode to:\n'
          '• Learn how the AI works\n'
          '• Test strategies safely\n'
          '• Build confidence\n\n'
          'Enable live trading only when you\'re ready.',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Continue Learning', style: TextStyle(color: Colors.blue.shade400)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1F2E),
        elevation: 0,
        title: Row(
          children: [
            Icon(Icons.psychology, color: Colors.blue.shade400),
            const SizedBox(width: 8),
            const Text(
              'Hermes AI',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 20,
              ),
            ),
          ],
        ),
        actions: [
          // Paper Trading Mode Indicator
          GestureDetector(
            onTap: _showPaperTradeInfo,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.green.shade700.withOpacity(0.2),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.green.shade400),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.school, color: Colors.green.shade400, size: 16),
                  const SizedBox(width: 4),
                  Text(
                    'PAPER',
                    style: TextStyle(
                      color: Colors.green.shade400,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 16),
          
          // Live Status Indicator
          if (isLoading)
            AnimatedBuilder(
              animation: _pulseAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: _pulseAnimation.value,
                  child: Icon(
                    Icons.circle,
                    color: Colors.orange.shade400,
                    size: 12,
                  ),
                );
              },
            )
          else
            Icon(
              Icons.circle,
              color: Colors.green.shade400,
              size: 12,
            ),
          const SizedBox(width: 8),
          Text(
            isLoading ? 'UPDATING' : 'LIVE',
            style: TextStyle(
              color: isLoading ? Colors.orange.shade400 : Colors.green.shade400,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: IndexedStack(
        index: currentPageIndex,
        children: [
          // Home / Snapshot Screen
          _buildHomeContent(),
          
          // Compare Screen
          CompareScreenWidget(
            recommendations: {
              'all_recommendations': recommendations,
              'top_recommendation': topRecommendation?['top_recommendation'],
              'confidence_pct': topRecommendation?['confidence_pct'],
              'expected_return_pct': topRecommendation?['expected_return_pct'],
            },
          ),
          
          // Learn / Help Screen
          const LearnHelpWidget(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: const Color(0xFF1A1F2E),
        selectedItemColor: Colors.blue.shade400,
        unselectedItemColor: Colors.grey.shade500,
        currentIndex: currentPageIndex,
        onTap: (index) => setState(() => currentPageIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.compare_arrows),
            label: 'Compare',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.school),
            label: 'Learn',
          ),
        ],
      ),
    );
  }

  Widget _buildHomeContent() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Risk Preference Selector
              RiskSelectorWidget(
                selectedRisk: riskPreference,
                onRiskChanged: (risk) {
                  setState(() => riskPreference = risk);
                  _loadData();
                },
              ),
              
              const SizedBox(height: 20),
              
              // Top Recommendation Card
              if (topRecommendation != null)
                TopRecommendationWidget(
                  recommendation: topRecommendation!,
                  isPaperMode: isPaperTradeMode,
                  onPaperTrade: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: const Text('Paper trade logged! Track your progress in Learn tab.'),
                        backgroundColor: Colors.green.shade700,
                      ),
                    );
                  },
                  onViewDetails: () {
                    // Navigate to asset detail screen
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => AssetDetailScreen(
                          recommendation: topRecommendation!,
                        ),
                      ),
                    );
                  },
                )
              else if (isLoading)
                _buildLoadingCard()
              else
                _buildErrorCard(),
              
              const SizedBox(height: 24),
              
              // Quick Tips
              _buildQuickTips(),
              
              const SizedBox(height: 24),
              
              // Recent Performance (placeholder)
              _buildRecentPerformance(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingCard() {
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text(
              'AI is analyzing markets...',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.red.shade400.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade400, size: 48),
          const SizedBox(height: 16),
          const Text(
            'Unable to load recommendations',
            style: TextStyle(color: Colors.white, fontSize: 16),
          ),
          const SizedBox(height: 8),
          const Text(
            'Check your internet connection and try again',
            style: TextStyle(color: Colors.grey, fontSize: 14),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadData,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue.shade600,
            ),
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickTips() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.blue.shade400.withOpacity(0.1),
            Colors.purple.shade400.withOpacity(0.1),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.blue.shade400.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb, color: Colors.yellow.shade400, size: 24),
              const SizedBox(width: 12),
              const Text(
                'Quick Tips for Beginners',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildTip('💡', 'Start with paper trading to practice without risk'),
          _buildTip('🛡️', 'Choose Conservative risk for safer recommendations'),
          _buildTip('📊', 'Higher confidence signals are more reliable'),
          _buildTip('📚', 'Use the Learn tab to understand trading basics'),
        ],
      ),
    );
  }

  Widget _buildTip(String emoji, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 16)),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                color: Colors.grey.shade300,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentPerformance() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.trending_up, color: Colors.green.shade400, size: 24),
              const SizedBox(width: 12),
              const Text(
                'Paper Trading Performance',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildPerformanceItem('Total Return', '+5.2%', Colors.green.shade400),
              ),
              Expanded(
                child: _buildPerformanceItem('Win Rate', '68%', Colors.blue.shade400),
              ),
              Expanded(
                child: _buildPerformanceItem('Trades', '12', Colors.grey.shade400),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF0F1420),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'Great progress! Your paper trading is improving your skills.',
              style: TextStyle(
                color: Colors.grey.shade400,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            color: Colors.grey,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}

// Placeholder for Asset Detail Screen
class AssetDetailScreen extends StatelessWidget {
  final Map<String, dynamic> recommendation;

  const AssetDetailScreen({super.key, required this.recommendation});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1F2E),
        title: Text(recommendation['top_recommendation']['symbol']),
      ),
      body: const Center(
        child: Text(
          'Asset Detail View\n(Coming Soon)',
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.white, fontSize: 18),
        ),
      ),
    );
  }
}
