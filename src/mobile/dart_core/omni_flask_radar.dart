// Omni FLASK Radar Chart Widget (Dart)
// Ref: kaistAI/FLASK — ICLR 2024
class SkillPoint { final String name; final double score; SkillPoint({required this.name, required this.score}); }
class FlaskRadarData { final String model; final List<SkillPoint> skills;
  FlaskRadarData({required this.model, required this.skills});
  double get overall => skills.isEmpty ? 0 : skills.fold(0.0, (a, s) => a + s.score) / skills.length;
}

class OmniFlaskRadar {
  static List<double> normalizeScores(List<SkillPoint> skills, {double maxScore = 5.0}) {
    return skills.map((s) => s.score / maxScore).toList();
  }
  static String winner(List<FlaskRadarData> models) {
    if (models.isEmpty) return '';
    models.sort((a, b) => b.overall.compareTo(a.overall));
    return models.first.model;
  }
}
