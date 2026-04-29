// Omni DMax Mobile Monitor (Dart)
// Ref: czg1225/DMax
class DMaxDecodeResult { final int nParallel; final double acceptRate;
  DMaxDecodeResult({required this.nParallel, required this.acceptRate}); }
class OmniDMaxMobile {
  static DMaxDecodeResult monitor(List<int> proposed, List<int> verified) {
    int accepted = 0;
    for (int i = 0; i < proposed.length && i < verified.length; i++) {
      if (proposed[i] == verified[i]) accepted++; else break;
    }
    return DMaxDecodeResult(nParallel: accepted,
      acceptRate: accepted / (proposed.isEmpty ? 1 : proposed.length));
  }
}
