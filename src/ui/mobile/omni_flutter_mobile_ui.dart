// OMNI UI & Mobile Layer
// Flutter Mobile Interface
// Based on flutter/flutter. Provides cross-platform native UI compilation mapped to Omni Engine.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';

/// Flutter Bridge to the Universal Binary via MethodChannels.
class OmniFlutterBridge {
  static const MethodChannel _channel = MethodChannel('omni_universal_binary');

  static Future<Map<String, dynamic>> executeCommand(String command, Map<String, dynamic> payload) async {
    try {
      print("OMNI Dart: Dispatching command '$command' to native C-ABI via MethodChannel.");
      final String resultJson = await _channel.invokeMethod('executeOmniCommand', {
        'command': command,
        'payload': jsonEncode(payload)
      });
      return jsonDecode(resultJson);
    } on PlatformException catch (e) {
      print("OMNI Dart Error: Native execution failed - ${e.message}");
      return {'error': e.message, 'status': 'failed'};
    }
  }
}

class OmniMobileDashboard extends StatefulWidget {
  @override
  _OmniMobileDashboardState createState() => _OmniMobileDashboardState();
}

class _OmniMobileDashboardState extends State<OmniMobileDashboard> {
  String _engineStatus = 'Unknown';
  bool _isLoading = false;

  Future<void> _checkEngineStatus() async {
    setState(() { _isLoading = true; });
    
    final result = await OmniFlutterBridge.executeCommand('system.status', {});
    
    setState(() {
      _isLoading = false;
      if (result['status'] == 'success') {
        _engineStatus = "Online (v${result['version']})";
      } else {
        _engineStatus = "Error: ${result['error']}";
      }
    });
  }

  @override
  void initState() {
    super.initState();
    _checkEngineStatus();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('OMNI Universal Mobile'),
        backgroundColor: Colors.black87,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text('Native Engine Status:', style: TextStyle(fontSize: 18, color: Colors.grey)),
            SizedBox(height: 10),
            _isLoading 
                ? CircularProgressIndicator() 
                : Text(_engineStatus, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 40),
            ElevatedButton(
              onPressed: _checkEngineStatus,
              child: Text('Refresh Status'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15)
              ),
            )
          ],
        ),
      ),
    );
  }
}

void main() {
  runApp(MaterialApp(
    theme: ThemeData.dark(),
    home: OmniMobileDashboard(),
  ));
}
