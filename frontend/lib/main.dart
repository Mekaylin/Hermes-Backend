import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'services/api_service.dart';
import 'providers/trading_data_provider.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const HermesApp());
}

class HermesApp extends StatelessWidget {
  const HermesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiService>(
          create: (_) => ApiService(),
        ),
        ChangeNotifierProxyProvider<ApiService, TradingDataProvider>(
          create: (context) => TradingDataProvider(Provider.of<ApiService>(context, listen: false)),
          update: (context, apiService, previous) {
            previous?.apiService = apiService;
            return previous ?? TradingDataProvider(apiService);
          },
        ),
      ],
      child: MaterialApp(
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
      ),
    );
  }
}
