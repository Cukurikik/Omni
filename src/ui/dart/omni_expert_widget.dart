import 'package:flutter/material.dart';

// OMNI MOTHER: Dart Expert Widget

class OmniExpertWidget extends StatelessWidget {
  final String id;
  final String status;

  OmniExpertWidget({required this.id, required this.status});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: status == 'ONLINE' ? Colors.green[900] : Colors.red[900],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text(id, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            SizedBox(height: 8),
            Text(status),
          ],
        ),
      ),
    );
  }
}
