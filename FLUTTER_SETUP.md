# 🚀 Hermes Flutter App Setup Guide

## Current Status

✅ Flutter installed (v3.35.2)  
✅ Dependencies installed  
✅ FlutterFire CLI installed  
🔄 Firebase configuration needed  

---

## Quick Start Commands

### 1. Add FlutterFire to Your PATH

```bash
# Add this line to your ~/.zshrc file
echo 'export PATH="$PATH":"$HOME/.pub-cache/bin"' >> ~/.zshrc

# Reload your shell
source ~/.zshrc

# Verify it works
flutterfire --version
```

### 2. Configure Firebase

```bash
cd frontend

# Login to Firebase
firebase login

# Configure your Flutter app with Firebase
# This will prompt you to select your Firebase project
flutterfire configure

# Follow the prompts:
# - Select your Firebase project (or create a new one)
# - Select platforms: iOS, Android, Web (all recommended)
# - This will create firebase_options.dart automatically
```

### 3. Update pubspec.yaml

Add Firebase dependencies to `frontend/pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Existing dependencies
  http: ^1.2.0
  fl_chart: ^0.65.0
  provider: ^6.0.0
  intl: ^0.19.0
  cupertino_icons: ^1.0.2
  
  # Add these Firebase dependencies:
  firebase_core: ^3.1.0
  firebase_auth: ^5.1.0
  cloud_firestore: ^5.0.0
  firebase_analytics: ^11.0.0
  
  # Optional but useful:
  shared_preferences: ^2.2.0  # For local storage
  connectivity_plus: ^5.0.0   # Check internet connection
```

Then run:
```bash
flutter pub get
```

### 4. Initialize Firebase in Your App

Update `frontend/lib/main.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'screens/home_screen.dart';

void main() async {
  // Ensure Flutter is initialized
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
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
```

### 5. Create API Service Configuration

Create `frontend/lib/config/app_config.dart`:

```dart
class AppConfig {
  // Backend API Configuration
  static const String apiBaseUrl = 'https://hermes-backend-5s2l.onrender.com';
  
  // Local development
  static const String localApiUrl = 'http://localhost:8000';
  
  // Use this to switch between production and development
  static const bool isProduction = true;
  
  static String get baseUrl => isProduction ? apiBaseUrl : localApiUrl;
  
  // API Endpoints
  static String get healthEndpoint => '$baseUrl/health';
  static String marketEndpoint(String symbol) => '$baseUrl/market/$symbol/current';
  static String get predictionsEndpoint => '$baseUrl/predictions/generate';
  static String get assetsEndpoint => '$baseUrl/assets';
}
```

### 6. Update API Service

Update `frontend/lib/api_service.dart` to use the config:

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'config/app_config.dart';

class ApiService {
  // Test backend connection
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse(AppConfig.healthEndpoint),
        headers: {'Content-Type': 'application/json'},
      );
      return response.statusCode == 200;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }

  // Get market data
  Future<Map<String, dynamic>?> getMarketData(String symbol) async {
    try {
      final response = await http.get(
        Uri.parse(AppConfig.marketEndpoint(symbol)),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Error fetching market data: $e');
      return null;
    }
  }

  // Generate prediction
  Future<Map<String, dynamic>?> generatePrediction({
    required String symbol,
    required String timeframe,
    required int periods,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(AppConfig.predictionsEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'symbol': symbol,
          'timeframe': timeframe,
          'periods': periods,
        }),
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Error generating prediction: $e');
      return null;
    }
  }
}
```

---

## Running Your Flutter App

### For Web (easiest to test):
```bash
cd frontend
flutter run -d chrome
```

### For iOS Simulator:
```bash
cd frontend
open -a Simulator  # Open iOS Simulator first
flutter run -d ios
```

### For Android Emulator:
```bash
cd frontend
# Make sure Android emulator is running
flutter run -d android
```

### For macOS Desktop:
```bash
cd frontend
flutter run -d macos
```

---

## Firebase Console Setup (Do This First!)

### 1. Create Firestore Database

1. Go to your Firebase Console: https://console.firebase.google.com
2. Select your project (or create a new one)
3. Click **Firestore Database** in the left menu
4. Click **Create database**
5. Choose **Start in production mode**
6. Select a location (e.g., `us-central1`)
7. Click **Enable**

### 2. Set Up Firestore Rules

In Firestore Database → Rules, paste this:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isOwner(userId) {
      return isAuthenticated() && request.auth.uid == userId;
    }
    
    // Users
    match /users/{userId} {
      allow read: if isAuthenticated();
      allow write: if isOwner(userId);
    }
    
    // Portfolios
    match /portfolios/{portfolioId} {
      allow read, write: if isAuthenticated() && 
        resource.data.userId == request.auth.uid;
    }
    
    // Predictions
    match /predictions/{predictionId} {
      allow read, write: if isAuthenticated() && 
        resource.data.userId == request.auth.uid;
    }
    
    // Watchlists
    match /watchlists/{watchlistId} {
      allow read, write: if isAuthenticated() && 
        resource.data.userId == request.auth.uid;
    }
  }
}
```

### 3. Enable Authentication

1. Go to **Authentication** in Firebase Console
2. Click **Get started**
3. Enable **Email/Password** sign-in
4. (Optional) Enable **Google** sign-in

### 4. Create Firestore Collections

In Firestore Database, create these collections:
- `users`
- `portfolios`
- `predictions`
- `watchlists`

---

## Troubleshooting

### FlutterFire command not found?
```bash
# Add to PATH
export PATH="$PATH":"$HOME/.pub-cache/bin"
source ~/.zshrc
```

### Firebase login issues?
```bash
# Install Firebase CLI if not installed
npm install -g firebase-tools

# Login
firebase login
```

### CocoaPods issues (iOS)?
```bash
cd frontend/ios
pod install
cd ..
flutter clean
flutter pub get
```

### Build errors?
```bash
flutter clean
flutter pub get
flutter pub upgrade
```

---

## Next Steps After Setup

1. ✅ Configure Firebase with `flutterfire configure`
2. ✅ Add Firebase dependencies to pubspec.yaml
3. ✅ Update main.dart with Firebase initialization
4. ✅ Create API service configuration
5. ✅ Run the app: `flutter run -d chrome`
6. ✅ Test connection to backend
7. ✅ Set up authentication UI
8. ✅ Test with real market data

---

## Your Current Backend

**Production:** https://hermes-backend-5s2l.onrender.com  
**Local:** http://localhost:8000 (running)  

**Test endpoints:**
```bash
# Health check
curl https://hermes-backend-5s2l.onrender.com/health

# Market data
curl https://hermes-backend-5s2l.onrender.com/market/BTCUSDT/current
```

---

## Quick Commands Reference

```bash
# Start Flutter app (web)
cd frontend && flutter run -d chrome

# Start backend (if not running)
cd backend && .venv/bin/python3 -m uvicorn simple_main:app --port 8000

# Check Flutter doctor
flutter doctor

# Update dependencies
cd frontend && flutter pub upgrade

# Clean build
flutter clean && flutter pub get
```

---

**Ready to go! Start with Step 1 (add FlutterFire to PATH) and work through the steps.** 🚀
