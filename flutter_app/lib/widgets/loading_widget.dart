import 'package:flutter/material.dart';

class LoadingWidget extends StatefulWidget {
  final String message;
  
  const LoadingWidget({
    super.key,
    this.message = 'Loading...',
  });

  @override
  State<LoadingWidget> createState() => _LoadingWidgetState();
}

class _LoadingWidgetState extends State<LoadingWidget>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();
    _animation = Tween<double>(begin: 0, end: 1).animate(_controller);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F2E),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2A2F3E)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AnimatedBuilder(
            animation: _animation,
            builder: (context, child) {
              return Transform.rotate(
                angle: _animation.value * 2 * 3.14159,
                child: Icon(
                  Icons.psychology,
                  color: Colors.blue.shade400,
                  size: 32,
                ),
              );
            },
          ),
          const SizedBox(height: 16),
          Text(
            widget.message,
            style: TextStyle(
              color: Colors.grey.shade300,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
