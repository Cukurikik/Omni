import 'package:flutter/material.dart';

class OmniDashboardWidget extends StatelessWidget {
  final String clusterStatus;
  final int activeNodes;

  const OmniDashboardWidget({
    Key? key,
    required this.clusterStatus,
    required this.activeNodes,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              "OMNI Nexus Cluster Status",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Status:", style: TextStyle(fontSize: 16)),
                Chip(
                  label: Text(clusterStatus, style: const TextStyle(color: Colors.white)),
                  backgroundColor: clusterStatus == "HEALTHY" ? Colors.green : Colors.red,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Active Nodes:", style: TextStyle(fontSize: 16)),
                Text("$activeNodes", style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
