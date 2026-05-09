import 'package:flutter/material.dart';

// OMNI MOTHER: Mobile Node Details View

class OmniNodeDetails extends StatelessWidget {
  final String nodeId;
  OmniNodeDetails(this.nodeId);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(Icons.computer),
        title: Text('Node: $nodeId'),
        subtitle: Text('Status: Healthy | VRAM: 72GB/80GB'),
      ),
    );
  }
}
