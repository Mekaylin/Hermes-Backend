import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const HermesApp());
}

class HermesApp extends StatelessWidget {
  const HermesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hermes AI Market Analysis',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0A0E1A),
        cardColor: const Color(0xFF1A1F2E),
        canvasColor: const Color(0xFF1A1F2E),
        fontFamily: 'SF Pro Display',
      ),
      home: const HomeScreen(),
    );
  }
}
