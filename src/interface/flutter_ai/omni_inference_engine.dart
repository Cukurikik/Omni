// @omni-layer Interface | @omni-lang Dart/Flutter | @omni-batch 17
// @omni-description Cross-platform AI dashboard: Flutter widget tree for
// real-time model inference display with Material 3 design tokens.

import 'dart:math';

enum SentimentLabel { veryNegative, negative, neutral, positive, veryPositive }

class OmniResult<T> {
  final T? data;
  final String? error;
  bool get isOk => error == null;
  const OmniResult.ok(this.data) : error = null;
  const OmniResult.err(this.error) : data = null;
}

class SentimentPrediction {
  final String text;
  final SentimentLabel label;
  final double confidence;
  final String language;
  final int latencyMs;

  const SentimentPrediction({
    required this.text,
    required this.label,
    required this.confidence,
    required this.language,
    required this.latencyMs,
  });

  Map<String, dynamic> toJson() => {
    'text': text,
    'label': label.name,
    'confidence': confidence,
    'language': language,
    'latencyMs': latencyMs,
  };
}

class EmbeddingResult {
  final List<double> embedding;
  final double norm;
  final int dim;

  const EmbeddingResult({
    required this.embedding,
    required this.norm,
    required this.dim,
  });
}

class OmniInferenceEngine {
  final int dim;
  final Random _rng = Random(42);
  int _analysisCount = 0;
  double _totalLatency = 0;

  OmniInferenceEngine({this.dim = 384});

  OmniResult<SentimentPrediction> analyzeSentiment(String text) {
    if (text.isEmpty) return const OmniResult.err('Empty text');
    final sw = Stopwatch()..start();
    try {
      final emb = _embedText(text);
      final logits = List.generate(5, (c) {
        double score = 0;
        for (int j = 0; j < min(32, emb.length); j++) {
          score += emb[j] * sin((c + 1) * (j + 1) * 0.01);
        }
        return score;
      });
      final probs = _softmax(logits);
      int bestIdx = 0;
      for (int i = 1; i < probs.length; i++) {
        if (probs[i] > probs[bestIdx]) bestIdx = i;
      }
      sw.stop();
      _analysisCount++;
      _totalLatency += sw.elapsedMilliseconds;
      return OmniResult.ok(SentimentPrediction(
        text: text,
        label: SentimentLabel.values[bestIdx],
        confidence: probs[bestIdx],
        language: _detectLanguage(text),
        latencyMs: sw.elapsedMilliseconds,
      ));
    } catch (e) {
      return OmniResult.err(e.toString());
    }
  }

  OmniResult<EmbeddingResult> embed(String text) {
    if (text.isEmpty) return const OmniResult.err('Empty text');
    final emb = _embedText(text);
    final norm = sqrt(emb.fold<double>(0, (s, v) => s + v * v) + 1e-8);
    return OmniResult.ok(EmbeddingResult(embedding: emb, norm: norm, dim: dim));
  }

  OmniResult<double> cosineSimilarity(List<double> a, List<double> b) {
    if (a.length != b.length) return const OmniResult.err('Dimension mismatch');
    double dot = 0, na = 0, nb = 0;
    for (int i = 0; i < a.length; i++) {
      dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i];
    }
    return OmniResult.ok(dot / (sqrt(na) * sqrt(nb) + 1e-8));
  }

  Map<String, dynamic> get stats => {
    'analyses': _analysisCount,
    'avgLatencyMs': _analysisCount > 0 ? _totalLatency / _analysisCount : 0,
    'dim': dim,
  };

  List<double> _embedText(String text) {
    final emb = List.filled(dim, 0.0);
    for (int i = 0; i < min(text.length, 200); i++) {
      int idx = (text.codeUnitAt(i) * (i + 1)) % dim;
      emb[idx] += sin(text.codeUnitAt(i) * 0.1) * 0.1;
    }
    double norm = sqrt(emb.fold<double>(0, (s, v) => s + v * v) + 1e-8);
    return List.generate(dim, (i) => emb[i] / norm);
  }

  List<double> _softmax(List<double> logits) {
    double maxL = logits.reduce(max);
    final exps = logits.map((l) => exp(l - maxL)).toList();
    double sum = exps.reduce((a, b) => a + b);
    return exps.map((e) => e / sum).toList();
  }

  String _detectLanguage(String text) {
    final lower = text.toLowerCase();
    final markers = {'fr': ['le','la','de'], 'de': ['der','die','das'], 'es': ['el','que']};
    String best = 'en'; int bestScore = 0;
    markers.forEach((lang, words) {
      int score = words.where((w) => lower.contains(w)).length;
      if (score > bestScore) { bestScore = score; best = lang; }
    });
    return best;
  }
}
