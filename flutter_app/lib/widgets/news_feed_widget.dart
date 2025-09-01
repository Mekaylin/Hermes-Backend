import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class NewsFeedWidget extends StatelessWidget {
  final List<Map<String, dynamic>> news;

  const NewsFeedWidget({super.key, required this.news});

  Color getSentimentColor(int sentiment) {
    switch (sentiment) {
      case 2:
        return Colors.green.shade400; // Positive
      case 0:
        return Colors.red.shade400; // Negative
      default:
        return Colors.yellow.shade600; // Neutral
    }
  }

  String getSentimentLabel(int sentiment) {
    switch (sentiment) {
      case 2:
        return 'BULLISH';
      case 0:
        return 'BEARISH';
      default:
        return 'NEUTRAL';
    }
  }

  IconData getSentimentIcon(int sentiment) {
    switch (sentiment) {
      case 2:
        return Icons.trending_up;
      case 0:
        return Icons.trending_down;
      default:
        return Icons.remove;
    }
  }

  String formatTime(String? timestamp) {
    if (timestamp == null) return 'Unknown';
    try {
      final dateTime = DateTime.parse(timestamp);
      final now = DateTime.now();
      final difference = now.difference(dateTime);
      
      if (difference.inMinutes < 60) {
        return '${difference.inMinutes}m ago';
      } else if (difference.inHours < 24) {
        return '${difference.inHours}h ago';
      } else {
        return '${difference.inDays}d ago';
      }
    } catch (e) {
      return 'Unknown';
    }
  }

  @override
  Widget build(BuildContext context) {
    if (news.isEmpty) {
      return Container(
        height: 100,
        decoration: BoxDecoration(
          color: const Color(0xFF0A0E1A),
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Center(
          child: Text(
            'No news available',
            style: TextStyle(color: Colors.grey),
          ),
        ),
      );
    }

    return Column(
      children: news.take(5).map((item) {
        final sentiment = item['sentiment'] ?? 1;
        final sentimentColor = getSentimentColor(sentiment);
        
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          decoration: BoxDecoration(
            color: const Color(0xFF0A0E1A),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: sentimentColor.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: InkWell(
            borderRadius: BorderRadius.circular(12),
            onTap: () {
              // TODO: Open article in browser or detail view
            },
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Sentiment indicator
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: sentimentColor.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Icon(
                          getSentimentIcon(sentiment),
                          color: sentimentColor,
                          size: 16,
                        ),
                      ),
                      const SizedBox(width: 12),
                      
                      // Article content
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item['title'] ?? 'No title',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                height: 1.3,
                              ),
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 8),
                            
                            // Source and time row
                            Row(
                              children: [
                                Text(
                                  item['source']?['name'] ?? 'Unknown Source',
                                  style: TextStyle(
                                    color: Colors.grey.shade400,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  '•',
                                  style: TextStyle(
                                    color: Colors.grey.shade600,
                                    fontSize: 12,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  formatTime(item['publishedAt']),
                                  style: TextStyle(
                                    color: Colors.grey.shade500,
                                    fontSize: 12,
                                  ),
                                ),
                                const Spacer(),
                                
                                // Sentiment badge
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 6,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: sentimentColor.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    getSentimentLabel(sentiment),
                                    style: TextStyle(
                                      color: sentimentColor,
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
