/// OMNI Interface Layer — Dart/Flutter Inference Client
/// Cross-platform mobile inference with isolate-based parallelism.

import 'dart:async';
import 'dart:isolate';
import 'dart:math';

/// Inference request
class InferenceRequest {
  final String prompt;
  final int maxTokens;
  final double temperature;
  final double topP;
  final bool stream;

  const InferenceRequest({
    required this.prompt,
    this.maxTokens = 256,
    this.temperature = 0.7,
    this.topP = 0.9,
    this.stream = false,
  });

  Map<String, dynamic> toJson() => {
    'prompt': prompt,
    'max_tokens': maxTokens,
    'temperature': temperature,
    'top_p': topP,
    'stream': stream,
  };
}

/// Inference response
class InferenceResponse {
  final String requestId;
  final String generatedText;
  final int tokensGenerated;
  final double latencyMs;
  final String finishReason;

  const InferenceResponse({
    required this.requestId,
    required this.generatedText,
    required this.tokensGenerated,
    required this.latencyMs,
    required this.finishReason,
  });

  factory InferenceResponse.fromJson(Map<String, dynamic> json) {
    return InferenceResponse(
      requestId: json['request_id'] ?? '',
      generatedText: json['generated_text'] ?? '',
      tokensGenerated: json['tokens_generated'] ?? 0,
      latencyMs: (json['latency_ms'] ?? 0).toDouble(),
      finishReason: json['finish_reason'] ?? 'unknown',
    );
  }
}

/// Softmax computation
List<double> softmax(List<double> logits) {
  final maxVal = logits.reduce(max);
  final exps = logits.map((x) => exp(x - maxVal)).toList();
  final sum = exps.reduce((a, b) => a + b);
  return exps.map((x) => x / sum).toList();
}

/// Top-p (nucleus) sampling
int topPSample(List<double> probs, double topP) {
  final indexed = List.generate(probs.length, (i) => MapEntry(i, probs[i]));
  indexed.sort((a, b) => b.value.compareTo(a.value));

  double cumProb = 0.0;
  final candidates = <MapEntry<int, double>>[];
  for (final entry in indexed) {
    cumProb += entry.value;
    candidates.add(entry);
    if (cumProb >= topP) break;
  }

  final total = candidates.fold(0.0, (sum, e) => sum + e.value);
  double r = Random().nextDouble() * total;
  for (final entry in candidates) {
    r -= entry.value;
    if (r <= 0) return entry.key;
  }
  return candidates.last.key;
}

/// OMNI Flutter Inference Engine
class OmniFlutterEngine {
  final String baseUrl;
  final String apiKey;
  final Duration timeout;

  OmniFlutterEngine({
    required this.baseUrl,
    required this.apiKey,
    this.timeout = const Duration(seconds: 30),
  });

  /// Run inference in a background isolate for UI responsiveness
  Future<InferenceResponse> infer(InferenceRequest request) async {
    final stopwatch = Stopwatch()..start();
    final result = await Isolate.run(() => _processInference(request));
    stopwatch.stop();
    return InferenceResponse(
      requestId: DateTime.now().microsecondsSinceEpoch.toString(),
      generatedText: result,
      tokensGenerated: result.split(' ').length,
      latencyMs: stopwatch.elapsedMilliseconds.toDouble(),
      finishReason: 'stop',
    );
  }

  /// Stream tokens via SSE
  Stream<String> streamInfer(InferenceRequest request) async* {
    // In production: connect to SSE endpoint
    final words = request.prompt.split(' ');
    for (final word in words) {
      await Future.delayed(const Duration(milliseconds: 50));
      yield word;
    }
  }

  /// Compute text embeddings
  Future<List<double>> embed(String text) async {
    return await Isolate.run(() {
      // Production: call embedding model
      final rng = Random(text.hashCode);
      return List.generate(768, (_) => rng.nextDouble() * 2 - 1);
    });
  }

  /// Cosine similarity between two vectors
  static double cosineSimilarity(List<double> a, List<double> b) {
    double dot = 0, normA = 0, normB = 0;
    for (int i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    return dot / (sqrt(normA) * sqrt(normB));
  }
}

String _processInference(InferenceRequest request) {
  // Production: actual on-device inference via FFI
  return 'Generated: ${request.prompt.substring(0, min(50, request.prompt.length))}';
}
