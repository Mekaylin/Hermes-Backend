import 'package:flutter/material.dart';
import 'dart:async';
import '../widgets/top_recommendation_widget.dart';
import '../widgets/risk_selector_widget.dart';
import '../widgets/compare_screen_widget.dart';
import '../widgets/learn_help_widget.dart';
import '../api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  String riskPreference = 'Conservative';
  bool isPaperTradeMode = true;
  bool isLoading = false;
  Map<String, dynamic>? topRecommendation;
  List<dynamic> recommendations = [];
  int currentPageIndex = 0;
  Timer? _refreshTimer;
  
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
    
    _loadData();
    _startAutoRefresh();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _pulseController.dispose();
    super.dispose();
  }

  void _startAutoRefresh() {
    _refreshTimer = Timer.periodic(const Duration(minutes: 2), (timer) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    if (mounted) {
      setState(() => isLoading = true);
    }
    
    try {
      final topRec = await ApiService.fetchTopRecommendation(riskPreference);
      final recs = await ApiService.fetchRecommendations(riskPreference, 5);
      
      if (mounted) {
        setState(() {
          topRecommendation = topRec;
          recommendations = recs;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Unable to load recommendations: ${e.toString()}'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => isLoading = false);
      }
    }
  }

  void _showHelpDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1F2E),
        title: const Text(
          'About Confidence & Risk',
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          'Confidence = how sure the AI is based on past performance.\n\n'
          'Risk levels:\n'
          '• Green (Low) = stable assets\n'
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
          // Paper Trade Mode Indicator
          GestureDetector(
            onTap: _showPaperTradeInfo,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              margin: const EdgeInsets.only(right: 8),
              decoration: BoxDecoration(
                color: Colors.green.shade900.withOpacity(0.3),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.green.shade400),
              ),
              child: Row(
                children: [
                  Icon(Icons.school, color: Colors.green.shade400, size: 16),
                  const SizedBox(width: 4),
                  Text(
                    'PAPER',
                    style: TextStyle(
                      color: Colors.green.shade400,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          // Live Status
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
          const SizedBox(width: 4),
          Text(
            isLoading ? 'LOADING' : 'LIVE',
            style: TextStyle(
              color: isLoading ? Colors.orange.shade400 : Colors.green.shade400,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
          IconButton(
            onPressed: _showHelpDialog,
            icon: Icon(Icons.help_outline, color: Colors.grey.shade400),
          ),
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
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_outline, color: Colors.yellow.shade600),
              const SizedBox(width: 8),
              const Text(
                'Quick Tips',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildTip('Start with Conservative risk level'),
          _buildTip('Always use stop-losses'),
          _buildTip('Paper trade first to learn'),
        ],
      ),
    );
  }

  Widget _buildTip(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(Icons.check_circle, color: Colors.green.shade400, size: 16),
          const SizedBox(width: 8),
          Text(
            text,
            style: const TextStyle(color: Colors.grey, fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentPerformance() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.trending_up, color: Colors.green.shade400),
              const SizedBox(width: 8),
              const Text(
                'Recent AI Performance',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildPerformanceMetric('Accuracy', '73.2%', Colors.green.shade400),
              _buildPerformanceMetric('Predictions', '247', Colors.blue.shade400),
              _buildPerformanceMetric('Avg Return', '+12.4%', Colors.orange.shade400),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceMetric(String label, String value, Color color) {
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

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  String selectedAsset = 'BTCUSDT';
  List<String> assets = ['BTCUSDT', 'ETHUSDT', 'AAPL', 'TSLA'];
  Timer? _timer;
  bool _isLoading = false;
  
  // Real-time data
  List<double> prices = [];
  List<double> aiTrend = [];
  String signal = 'HOLD';
  double confidence = 0.0;
  double targetPrice = 0.0;
  double currentPrice = 0.0;
  double priceChange = 0.0;
  double priceChangePercent = 0.0;
  List<Map<String, dynamic>> news = [];
  
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
    
    _loadData();
    _startAutoRefresh();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _pulseController.dispose();
    super.dispose();
  }

  void _startAutoRefresh() {
    _timer = Timer.periodic(const Duration(minutes: 1), (timer) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    
    try {
      // Load signal data
      final signalData = await ApiService.fetchSignal(selectedAsset);
      
      // Load news data
      final newsData = await ApiService.fetchNews(selectedAsset);
      
      // Load historical data for chart
      final historyData = await ApiService.fetchHistory(selectedAsset);
      
      setState(() {
        signal = signalData['signal']?.toString().toUpperCase() ?? 'HOLD';
        confidence = (signalData['confidence'] ?? 0.0).toDouble();
        targetPrice = (signalData['predicted_change'] ?? 0.0).toDouble() + currentPrice;
        news = List<Map<String, dynamic>>.from(newsData);
        
        // Generate sample chart data (replace with real data)
        prices = List.generate(60, (i) => 30000 + (i * 10.0) + (i % 5 * 50));
        aiTrend = List.generate(60, (i) => 30000 + (i * 12.0) + (i % 3 * 30));
        currentPrice = prices.isNotEmpty ? prices.last : 30000;
        priceChange = prices.length > 1 ? prices.last - prices[prices.length - 2] : 0;
        priceChangePercent = currentPrice > 0 ? (priceChange / currentPrice) * 100 : 0;
      });
    } catch (e) {
      // Handle error - use placeholder data
      setState(() {
        signal = 'HOLD';
        confidence = 0.5;
        currentPrice = 30000;
        targetPrice = 30120;
        priceChange = 120;
        priceChangePercent = 0.4;
        prices = List.generate(60, (i) => 30000 + i * 10.0);
        aiTrend = List.generate(60, (i) => 30000 + i * 12.0);
        news = [
          {
            'title': 'Bitcoin surges to new highs amid institutional adoption',
            'source': {'name': 'CryptoNews'},
            'sentiment': 2,
            'publishedAt': '2025-09-01T12:00:00Z'
          },
          {
            'title': 'Market uncertainty grows as inflation concerns mount',
            'source': {'name': 'MarketWatch'},
            'sentiment': 0,
            'publishedAt': '2025-09-01T11:30:00Z'
          },
          {
            'title': 'BTC remains stable despite global market volatility',
            'source': {'name': 'CoinDesk'},
            'sentiment': 1,
            'publishedAt': '2025-09-01T11:00:00Z'
          },
        ];
      });
    } finally {
      setState(() => _isLoading = false);
    }
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
            Icon(Icons.analytics, color: Colors.blue.shade400),
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
          if (_isLoading)
            AnimatedBuilder(
              animation: _pulseAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: _pulseAnimation.value,
                  child: Icon(
                    Icons.circle,
                    color: Colors.green.shade400,
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
            'LIVE',
            style: TextStyle(
              color: Colors.green.shade400,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            children: [
              // Asset Selector & Price Ticker
              Container(
                color: const Color(0xFF1A1F2E),
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: AssetSelector(
                            assets: assets,
                            selectedAsset: selectedAsset,
                            onChanged: (value) {
                              setState(() {
                                selectedAsset = value;
                              });
                              _loadData();
                            },
                          ),
                        ),
                        const SizedBox(width: 16),
                        IconButton(
                          onPressed: _loadData,
                          icon: Icon(
                            Icons.refresh,
                            color: Colors.blue.shade400,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    PriceTickerWidget(
                      currentPrice: currentPrice,
                      priceChange: priceChange,
                      priceChangePercent: priceChangePercent,
                    ),
                  ],
                ),
              ),
              
              // Main Content
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // AI Signal Widget
                    AISignalWidget(
                      signal: signal,
                      confidence: confidence,
                      targetPrice: targetPrice,
                      currentPrice: currentPrice,
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Market Chart
                    Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFF1A1F2E),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF2A2F3E)),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.show_chart, color: Colors.blue.shade400),
                              const SizedBox(width: 8),
                              const Text(
                                'Price Chart',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const Spacer(),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.orange.shade900.withOpacity(0.3),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  'AI TREND',
                                  style: TextStyle(
                                    color: Colors.orange.shade400,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          MarketChartWidget(
                            prices: prices,
                            aiTrend: aiTrend,
                            selectedAsset: selectedAsset,
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Portfolio Summary (placeholder)
                    PortfolioSummaryWidget(),
                    
                    const SizedBox(height: 20),
                    
                    // News Feed
                    Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFF1A1F2E),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF2A2F3E)),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.article, color: Colors.blue.shade400),
                              const SizedBox(width: 8),
                              const Text(
                                'Market News',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const Spacer(),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.purple.shade900.withOpacity(0.3),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  'AI SENTIMENT',
                                  style: TextStyle(
                                    color: Colors.purple.shade400,
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          NewsFeedWidget(news: news),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
