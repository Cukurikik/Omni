// Omni FollowBench Mobile (Dart)
// Mobile: Constraint satisfaction display.
// Ref: YJiangcm/FollowBench
class ConstraintResult { final String type; final bool satisfied; final double csr;
  ConstraintResult({required this.type, required this.satisfied, required this.csr}); }
class OmniFollowBenchMobile {
  static double computeCSR(List<ConstraintResult> results) {
    if (results.isEmpty) return 0.0;
    final satisfied = results.where((r) => r.satisfied).length;
    return satisfied / results.length;
  }
}
