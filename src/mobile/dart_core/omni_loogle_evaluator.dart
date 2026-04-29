// Omni LooGLE Evaluator (Dart)
// Mobile/Web Layer: Pure Dart logic for validating context metrics across Flutter platforms.

class LoogleEvalResult {
  final bool success;
  final double score;
  final String error;

  LoogleEvalResult._({required this.success, required this.score, required this.error});

  factory LoogleEvalResult.ok(double score) => LoogleEvalResult._(success: true, score: score, error: "");
  factory LoogleEvalResult.err(String error) => LoogleEvalResult._(success: false, score: 0.0, error: error);
}

class OmniLoogleEvaluator {
  static LoogleEvalResult evaluateRetrieval(int contextLength, int retrievedIndex) {
    if (contextLength <= 0) {
      return LoogleEvalResult.err("Context length must be > 0");
    }
    
    if (retrievedIndex < 0 || retrievedIndex >= contextLength) {
      return LoogleEvalResult.err("Retrieved index out of bounds");
    }

    double accuracy = 1.0 - (retrievedIndex / contextLength);
    return LoogleEvalResult.ok(accuracy);
  }
}
