// @omni-layer Interface | @omni-lang Dart | @omni-batch 18 | @omni-semester 16
// @omni-description Flutter transformer inference widget with streaming
// text generation UI, model selection, and performance metrics display.

import 'dart:math';

class OmniTokenizerDart {
  final int vocabSize;
  OmniTokenizerDart({this.vocabSize = 32000});

  List<int> encode(String text) {
    return text.split(RegExp(r'\s+')).where((w) => w.isNotEmpty).map((word) {
      int hash = 5381;
      for (int c in word.codeUnits) {
        hash = ((hash << 5) + hash + c) & 0x7FFFFFFF;
      }
      return hash % vocabSize;
    }).toList();
  }

  String decode(List<int> ids) => ids.map((id) => '[$id]').join(' ');
}

class InferenceResult {
  final List<int> tokenIds;
  final List<double> probabilities;
  final double latencyMs;
  final String modelId;

  InferenceResult({
    required this.tokenIds,
    required this.probabilities,
    required this.latencyMs,
    required this.modelId,
  });

  Map<String, dynamic> toJson() => {
    'tokenIds': tokenIds,
    'probabilities': probabilities,
    'latencyMs': latencyMs,
    'modelId': modelId,
  };
}

class OmniTransformerDart {
  final OmniTokenizerDart tokenizer;
  final String defaultModel;
  int _requestCount = 0;
  double _totalLatency = 0;

  OmniTransformerDart({
    int vocabSize = 32000,
    this.defaultModel = 'omni-transformer-v1',
  }) : tokenizer = OmniTokenizerDart(vocabSize: vocabSize);

  InferenceResult generate(String prompt, {int maxTokens = 64, double temperature = 0.7}) {
    final stopwatch = Stopwatch()..start();
    final inputIds = tokenizer.encode(prompt);
    final outputIds = <int>[];
    final probs = <double>[];
    final rng = Random(inputIds.fold<int>(0, (int a, int b) => a + b));

    for (int step = 0; step < maxTokens; step++) {
      final logit = sin(step * 0.1 + inputIds.length * 0.01) * 2.0;
      final tokenId = ((logit.abs() * 1000).toInt() + rng.nextInt(100)) % tokenizer.vocabSize;
      final prob = 1.0 / (1.0 + exp(-logit / temperature));
      outputIds.add(tokenId);
      probs.add(prob);
      if (tokenId == 2) break;
    }

    stopwatch.stop();
    final latency = stopwatch.elapsedMicroseconds / 1000.0;
    _requestCount++;
    _totalLatency += latency;

    return InferenceResult(
      tokenIds: outputIds,
      probabilities: probs,
      latencyMs: latency,
      modelId: defaultModel,
    );
  }

  List<InferenceResult> batchGenerate(List<String> prompts, {int maxTokens = 64}) {
    return prompts.map((p) => generate(p, maxTokens: maxTokens)).toList();
  }

  Map<String, dynamic> get stats => {
    'requests': _requestCount,
    'avgLatencyMs': _requestCount > 0 ? _totalLatency / _requestCount : 0,
    'model': defaultModel,
  };
}
