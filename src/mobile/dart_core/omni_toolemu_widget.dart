// Omni ToolEmu Risk Widget (Dart)
class ToolRisk { final String tool; final double score; final String level;
  ToolRisk({required this.tool, required this.score, required this.level}); }
class OmniToolEmuWidget {
  static String riskLevel(double score) => score > 0.7 ? 'critical' : score > 0.4 ? 'high' : 'low';
  static List<ToolRisk> assessBatch(List<Map<String,dynamic>> tools) =>
    tools.map((t) => ToolRisk(tool: t['name']??'', score: (t['score'] as num).toDouble(), level: riskLevel((t['score'] as num).toDouble()))).toList();
}
