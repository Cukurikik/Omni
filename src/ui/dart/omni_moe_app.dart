import 'package:flutter/material.dart';

// OMNI MOTHER: Dart Flutter Cross-Platform App

void main() {
  runApp(OmniMoEApp());
}

class OmniMoEApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Omni MoE Mobile',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
      ),
      home: Scaffold(
        appBar: AppBar(title: Text('OMNI Control Plane')),
        body: Center(
          child: Text('MoE Cluster: ONLINE', style: TextStyle(fontSize: 24)),
        ),
      ),
    );
  }
}
