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
  String riskPreference = 'Low'; // Conservative
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
