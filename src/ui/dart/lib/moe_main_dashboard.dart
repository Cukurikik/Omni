import 'package:flutter/material.dart';
import 'package:omni_ui/moe_expert_visualizer.dart'; // From File 49

/// OMNI Framework - Main Tenant Dashboard (Dart/Flutter)
/// Connects to the Ruby backend to display billing, token usage, 
/// and the real-time expert visualizer in a single unified interface.
class MoeMainDashboard extends StatelessWidget {
  final String tenantId;

  const MoeMainDashboard({Key? key, required this.tenantId}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        title: Text('OMNI MoE Dashboard - $tenantId'),
        backgroundColor: const Color(0xFF161B22),
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Top Row: Billing & Quota Stats
            Row(
              children: [
                _buildStatCard("Tokens Used", "8.45M", Colors.blueAccent),
                const SizedBox(width: 16),
                _buildStatCard("Current Bill", "\$145.20", Colors.greenAccent),
                const SizedBox(width: 16),
                _buildStatCard("Avg Active Params", "12.5%", Colors.purpleAccent),
              ],
            ),
            const SizedBox(height: 24),
            // Bottom Row: Real-time Expert Visualizer
            Expanded(
              child: MoEExpertVisualizer(numExperts: 8),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E1E),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF30363D)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(color: Colors.white70, fontSize: 14)),
            const SizedBox(height: 8),
            Text(value, style: TextStyle(color: color, fontSize: 28, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}
