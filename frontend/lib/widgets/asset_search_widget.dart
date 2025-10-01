import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/trading_data.dart';
import '../providers/trading_data_provider.dart';
import '../services/api_service.dart';

class AssetSearchWidget extends StatefulWidget {
  const AssetSearchWidget({super.key});

  @override
  State<AssetSearchWidget> createState() => _AssetSearchWidgetState();
}

class _AssetSearchWidgetState extends State<AssetSearchWidget> {
  final TextEditingController _searchController = TextEditingController();
  List<Asset> _searchResults = [];
  bool _isSearching = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _performSearch(String query) async {
    if (query.isEmpty) {
      setState(() {
        _searchResults = [];
      });
      return;
    }

    setState(() {
      _isSearching = true;
    });

    final dataProvider = Provider.of<TradingDataProvider>(context, listen: false);
    
    // First search in cached assets
    final cachedResults = dataProvider.searchAssets(query);
    
    setState(() {
      _searchResults = cachedResults;
      _isSearching = false;
    });
  }

  void _selectAsset(Asset asset) {
    final dataProvider = Provider.of<TradingDataProvider>(context, listen: false);
    final apiService = Provider.of<ApiService>(context, listen: false);
    
    dataProvider.setSelectedAsset(asset);
    
    // Load market data for selected asset
    _loadMarketData(asset.symbol, apiService, dataProvider);
    
    // Clear search
    _searchController.clear();
    setState(() {
      _searchResults = [];
    });
  }

  Future<void> _loadMarketData(String symbol, ApiService apiService, TradingDataProvider dataProvider) async {
    dataProvider.setLoading(true);
    
    try {
      // Load market data
      final marketData = await apiService.getCurrentMarketData(symbol);
      dataProvider.setMarketData(marketData);
      
      // Generate trading signal
      final signal = await apiService.generatePrediction(symbol: symbol);
      dataProvider.setTradingSignal(signal);
    } catch (e) {
      dataProvider.setError('Failed to load data for $symbol: $e');
    }
    
    dataProvider.setLoading(false);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Search Bar
        Container(
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
            ),
          ),
          child: TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: 'Search assets (BTC, EUR/USD, AAPL...)',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _isSearching
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: Padding(
                        padding: EdgeInsets.all(12.0),
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    )
                  : _searchController.text.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _searchController.clear();
                            _performSearch('');
                          },
                        )
                      : null,
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 12,
              ),
            ),
            onChanged: _performSearch,
          ),
        ),
        
        // Search Results
        if (_searchResults.isNotEmpty) ...[
          const SizedBox(height: 8),
          Container(
            constraints: const BoxConstraints(maxHeight: 200),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
              ),
            ),
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: _searchResults.length,
              itemBuilder: (context, index) {
                final asset = _searchResults[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: _getCategoryColor(asset.category),
                    child: Text(
                      asset.symbol.substring(0, 2).toUpperCase(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  title: Text(
                    asset.symbol,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(asset.name),
                  trailing: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getCategoryColor(asset.category).withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _getCategoryName(asset.category),
                      style: TextStyle(
                        color: _getCategoryColor(asset.category),
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  onTap: () => _selectAsset(asset),
                );
              },
            ),
          ),
        ],
      ],
    );
  }

  Color _getCategoryColor(AssetCategory category) {
    switch (category) {
      case AssetCategory.crypto:
        return Colors.orange;
      case AssetCategory.forex:
        return Colors.blue;
      case AssetCategory.stocks:
        return Colors.green;
      case AssetCategory.commodities:
        return Colors.amber;
      case AssetCategory.indices:
        return Colors.purple;
    }
  }

  String _getCategoryName(AssetCategory category) {
    switch (category) {
      case AssetCategory.crypto:
        return 'Crypto';
      case AssetCategory.forex:
        return 'Forex';
      case AssetCategory.stocks:
        return 'Stocks';
      case AssetCategory.commodities:
        return 'Commodities';
      case AssetCategory.indices:
        return 'Indices';
    }
  }
}
