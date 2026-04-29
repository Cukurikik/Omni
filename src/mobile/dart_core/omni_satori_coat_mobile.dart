// Omni Satori COAT Mobile (Dart)
// Ref: satori-reasoning/Satori — ICML'25
class COATStep { final int step; final String action; final double confidence;
  COATStep({required this.step, required this.action, required this.confidence}); }
class OmniSatoriMobile {
  static String selectAction(double conf, int step, int maxSteps) {
    if (conf < 0.2 && step > maxSteps ~/ 2) return 'explore';
    if (conf < 0.4) return 'reflect';
    return 'continue';
  }
  static double reward(bool correct, int steps, int maxSteps) {
    final base = correct ? 1.0 : -0.5;
    return base + 0.1 * (1.0 - steps / maxSteps);
  }
}
