// Omni EasyRec Mobile (Dart)
// Mobile Layer: Recommendation display for cross-platform.
// Ref: HKUDS/EasyRec — EMNLP 2025
class RecommendationItem { final String itemId; final double score; final String title;
  RecommendationItem({required this.itemId, required this.score, required this.title});
  bool get isStrongMatch => score >= 0.8;
}
class OmniEasyRecMobile {
  static List<RecommendationItem> filterStrong(List<RecommendationItem> items) {
    return items.where((i) => i.isStrongMatch).toList()..sort((a, b) => b.score.compareTo(a.score));
  }
}
