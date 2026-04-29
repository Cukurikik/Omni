// Omni AlphaRec Mobile Widget (Dart)
// Ref: LehengTHU/AlphaRec — ICLR 2025
class RecItem { final String id; final double score; RecItem({required this.id, required this.score}); }
class OmniAlphaRecMobile {
  static List<RecItem> rankItems(List<RecItem> items) {
    items.sort((a, b) => b.score.compareTo(a.score));
    return items;
  }
  static double ndcgAtK(List<String> ranked, Set<String> relevant, int k) {
    double dcg = 0, idcg = 0;
    for (int i = 0; i < k; i++) {
      if (i < ranked.length && relevant.contains(ranked[i])) dcg += 1 / _log2(i + 2);
      if (i < relevant.length) idcg += 1 / _log2(i + 2);
    }
    return idcg == 0 ? 0 : dcg / idcg;
  }
  static double _log2(int n) => _ln(n.toDouble()) / _ln(2);
  static double _ln(double x) { double r = 0; double t = (x-1)/(x+1); double p = t;
    for (int i = 1; i < 50; i += 2) { r += p / i; p *= t * t; } return 2 * r; }
}
