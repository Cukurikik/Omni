// OMNI Mobile — Flutter Cluster Map Widget
import 'package:flutter/material.dart';

class OmniClusterMap extends StatelessWidget {
  final int activeNodes;
  final int offlineNodes;

  const OmniClusterMap({Key? key, required this.activeNodes, required this.offlineNodes}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.greenAccent, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Cluster Topography", style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildIndicator(Colors.green, "Active", activeNodes),
              _buildIndicator(Colors.red, "Offline", offlineNodes),
            ],
          ),
          SizedBox(height: 20),
          // Placeholder for visual grid
          Wrap(
            spacing: 5,
            runSpacing: 5,
            children: List.generate(activeNodes + offlineNodes, (index) {
              return Container(
                width: 20, height: 20,
                decoration: BoxDecoration(
                  color: index < activeNodes ? Colors.green : Colors.red,
                  shape: BoxShape.circle,
                ),
              );
            }),
          )
        ],
      ),
    );
  }

  Widget _buildIndicator(Color color, String label, int count) {
    return Column(
      children: [
        Text("$count", style: TextStyle(color: color, fontSize: 24, fontWeight: FontWeight.bold)),
        Text(label, style: TextStyle(color: Colors.white70)),
      ],
    );
  }
}
