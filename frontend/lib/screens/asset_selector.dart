import 'package:flutter/material.dart';

class AssetSelector extends StatelessWidget {
  final List<String> assets;
  final String selectedAsset;
  final ValueChanged<String> onChanged;

  const AssetSelector({
    super.key,
    required this.assets,
    required this.selectedAsset,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0E1A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: selectedAsset,
          dropdownColor: const Color(0xFF1A1F2E),
          icon: Icon(
            Icons.keyboard_arrow_down,
            color: Colors.blue.shade400,
          ),
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
          items: assets.map((asset) {
            return DropdownMenuItem(
              value: asset,
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: _getAssetColor(asset),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(asset),
                ],
              ),
            );
          }).toList(),
          onChanged: (value) {
            if (value != null) {
              onChanged(value);
            }
          },
        ),
      ),
    );
  }

  Color _getAssetColor(String asset) {
    switch (asset.substring(0, 3)) {
      case 'BTC':
        return Colors.orange.shade400;
      case 'ETH':
        return Colors.blue.shade400;
      case 'AAP':
        return Colors.grey.shade400;
      case 'TSL':
        return Colors.red.shade400;
      default:
        return Colors.purple.shade400;
    }
  }
}
