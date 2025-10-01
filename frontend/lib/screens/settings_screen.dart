import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/trading_data_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

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
                  'Settings',
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
                    'Customize your trading experience',
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
                  // AI Preferences
                  _buildAIPreferencesSection(),
                  const SizedBox(height: 24),

                  // Notifications
                  _buildNotificationsSection(),
                  const SizedBox(height: 24),

                  // Display Settings
                  _buildDisplaySection(),
                  const SizedBox(height: 24),

                  // Data & Privacy
                  _buildDataPrivacySection(),
                  const SizedBox(height: 24),

                  // About
                  _buildAboutSection(),
                  
                  const SizedBox(height: 100), // Bottom padding
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAIPreferencesSection() {
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
                  color: Colors.blue.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.psychology,
                  color: Colors.blue,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              const Text(
                'AI Preferences',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildSettingItem(
            'Signal Confidence Threshold',
            'Minimum confidence level for displaying signals',
            trailing: const Text(
              '70%',
              style: TextStyle(
                color: Colors.blue,
                fontWeight: FontWeight.w600,
              ),
            ),
            onTap: () => _showConfidenceThresholdDialog(),
          ),
          
          _buildSettingItem(
            'Risk Tolerance',
            'Set your preferred risk level for recommendations',
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'Moderate',
                style: TextStyle(
                  color: Colors.orange,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            onTap: () => _showRiskToleranceDialog(),
          ),
          
          _buildSettingItem(
            'Auto-refresh Signals',
            'Automatically update AI signals every 5 minutes',
            trailing: Switch(
              value: true,
              onChanged: (value) {},
              activeColor: Colors.blue,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationsSection() {
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
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.notifications,
                  color: Colors.green,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              const Text(
                'Notifications',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildSettingItem(
            'Trading Signals',
            'Get notified when new AI signals are generated',
            trailing: Switch(
              value: true,
              onChanged: (value) {},
              activeColor: Colors.green,
            ),
          ),
          
          _buildSettingItem(
            'Price Alerts',
            'Notifications for significant price movements',
            trailing: Switch(
              value: false,
              onChanged: (value) {},
              activeColor: Colors.green,
            ),
          ),
          
          _buildSettingItem(
            'Market News',
            'Important market updates and economic events',
            trailing: Switch(
              value: true,
              onChanged: (value) {},
              activeColor: Colors.green,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDisplaySection() {
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
                  color: Colors.purple.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.palette,
                  color: Colors.purple,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              const Text(
                'Display',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildSettingItem(
            'Theme',
            'Currently using dark theme (recommended for trading)',
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.grey.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'Dark',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            onTap: () => _showThemeDialog(),
          ),
          
          _buildSettingItem(
            'Currency Display',
            'Default currency for price displays',
            trailing: const Text(
              'USD',
              style: TextStyle(
                color: Colors.purple,
                fontWeight: FontWeight.w600,
              ),
            ),
            onTap: () => _showCurrencyDialog(),
          ),
          
          _buildSettingItem(
            'Chart Style',
            'Default chart type for market analysis',
            trailing: const Text(
              'Candlestick',
              style: TextStyle(
                color: Colors.purple,
                fontWeight: FontWeight.w600,
              ),
            ),
            onTap: () => _showChartStyleDialog(),
          ),
        ],
      ),
    );
  }

  Widget _buildDataPrivacySection() {
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
                  color: Colors.red.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.security,
                  color: Colors.red,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              const Text(
                'Data & Privacy',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildSettingItem(
            'Data Collection',
            'Help improve AI by sharing anonymous usage data',
            trailing: Switch(
              value: true,
              onChanged: (value) {},
              activeColor: Colors.red,
            ),
          ),
          
          _buildSettingItem(
            'Clear Cache',
            'Remove stored market data and AI model cache',
            trailing: const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white30,
              size: 16,
            ),
            onTap: () => _showClearCacheDialog(),
          ),
          
          _buildSettingItem(
            'Export Data',
            'Download your trading signals and portfolio data',
            trailing: const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white30,
              size: 16,
            ),
            onTap: () => _showExportDialog(),
          ),
        ],
      ),
    );
  }

  Widget _buildAboutSection() {
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
                  color: Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.info,
                  color: Colors.orange,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              const Text(
                'About',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          _buildSettingItem(
            'Version',
            'Current app version and build information',
            trailing: const Text(
              '1.0.0',
              style: TextStyle(
                color: Colors.orange,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          
          _buildSettingItem(
            'Privacy Policy',
            'Read our privacy policy and terms of service',
            trailing: const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white30,
              size: 16,
            ),
            onTap: () => _showPrivacyPolicy(),
          ),
          
          _buildSettingItem(
            'Support',
            'Get help and contact our support team',
            trailing: const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white30,
              size: 16,
            ),
            onTap: () => _showSupport(),
          ),
          
          _buildSettingItem(
            'Rate App',
            'Help us improve by rating the app',
            trailing: const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white30,
              size: 16,
            ),
            onTap: () => _showRateApp(),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingItem(
    String title, 
    String subtitle, {
    Widget? trailing,
    VoidCallback? onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        title: Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        subtitle: Text(
          subtitle,
          style: TextStyle(
            fontSize: 13,
            color: Colors.white.withOpacity(0.6),
          ),
        ),
        trailing: trailing,
        onTap: onTap,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        tileColor: const Color(0xFF0A0E1A).withOpacity(0.3),
      ),
    );
  }

  // Dialog methods
  void _showConfidenceThresholdDialog() {
    // Implementation for confidence threshold selector
  }

  void _showRiskToleranceDialog() {
    // Implementation for risk tolerance selector
  }

  void _showThemeDialog() {
    // Implementation for theme selector
  }

  void _showCurrencyDialog() {
    // Implementation for currency selector
  }

  void _showChartStyleDialog() {
    // Implementation for chart style selector
  }

  void _showClearCacheDialog() {
    // Implementation for clear cache confirmation
  }

  void _showExportDialog() {
    // Implementation for data export
  }

  void _showPrivacyPolicy() {
    // Implementation for privacy policy view
  }

  void _showSupport() {
    // Implementation for support contact
  }

  void _showRateApp() {
    // Implementation for app rating
  }
}
