import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() {
  runApp(MinimalApp());
}

class MinimalApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hermes Minimal',
      home: Scaffold(
        appBar: AppBar(title: const Text('Hermes Minimal')),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: MinimalHome(),
        ),
      ),
    );
  }
}

class MinimalHome extends StatefulWidget {
  @override
  _MinimalHomeState createState() => _MinimalHomeState();
}

class _MinimalHomeState extends State<MinimalHome> {
  String _status = 'idle';
  Map<String, dynamic>? _data;

  Future<void> _fetch() async {
    setState(() => _status = 'fetching');
    try {
      final r = await http.get(Uri.parse('http://localhost:8080/ai-input?symbol=BTCUSDT'));
      if (r.statusCode != 200) throw Exception('HTTP ${r.statusCode}');
      final j = jsonDecode(r.body) as Map<String, dynamic>;
      setState(() { _status = 'OK'; _data = j; });
    } catch (e) {
      setState(() { _status = 'error: $e'; _data = null; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ElevatedButton(onPressed: _fetch, child: const Text('Fetch AI Input')),
        const SizedBox(height: 12),
        Text('Status: $_status'),
        const SizedBox(height: 12),
        Expanded(child: SingleChildScrollView(child: Text(_data == null ? '-' : const JsonEncoder.withIndent('  ').convert(_data))))
      ],
    );
  }
}
