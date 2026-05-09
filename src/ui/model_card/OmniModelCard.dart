// OmniModelCard.dart — Model Card Widget for Flutter
// Inspired by: HuggingFace Model Cards + OMNI model dashboard
// Layer: Interface / Dart/Flutter
//
// Cross-platform model information display widget with
// architecture visualization, metrics, and deployment status.

import 'dart:math';

enum ModelStatus { training, validating, deployed, archived, failed }

enum ModelFramework { pytorch, tensorflow, onnx, omni, jax }

class ModelMetrics {
  final double accuracy;
  final double f1Score;
  final double latencyMs;
  final double throughputRps;
  final int parameterCount;
  final double modelSizeMb;
  final Map<String, double> customMetrics;

  const ModelMetrics({
    required this.accuracy,
    required this.f1Score,
    required this.latencyMs,
    required this.throughputRps,
    required this.parameterCount,
    required this.modelSizeMb,
    this.customMetrics = const {},
  });

  String get formattedParams {
    if (parameterCount >= 1e9) {
      return '${(parameterCount / 1e9).toStringAsFixed(1)}B';
    } else if (parameterCount >= 1e6) {
      return '${(parameterCount / 1e6).toStringAsFixed(1)}M';
    } else if (parameterCount >= 1e3) {
      return '${(parameterCount / 1e3).toStringAsFixed(1)}K';
    }
    return parameterCount.toString();
  }

  Map<String, dynamic> toJson() => {
    'accuracy': accuracy,
    'f1_score': f1Score,
    'latency_ms': latencyMs,
    'throughput_rps': throughputRps,
    'parameter_count': parameterCount,
    'model_size_mb': modelSizeMb,
    'custom_metrics': customMetrics,
  };
}

class ModelArchitecture {
  final String name;
  final int numLayers;
  final int hiddenSize;
  final int numHeads;
  final int vocabSize;
  final int maxSequenceLength;
  final List<String> modalities;

  const ModelArchitecture({
    required this.name,
    required this.numLayers,
    required this.hiddenSize,
    required this.numHeads,
    this.vocabSize = 0,
    this.maxSequenceLength = 2048,
    this.modalities = const ['text'],
  });

  String get summary =>
    '$name: ${numLayers}L/${numHeads}H/${hiddenSize}D (seq=$maxSequenceLength)';

  Map<String, dynamic> toJson() => {
    'name': name,
    'num_layers': numLayers,
    'hidden_size': hiddenSize,
    'num_heads': numHeads,
    'vocab_size': vocabSize,
    'max_sequence_length': maxSequenceLength,
    'modalities': modalities,
  };
}

class ModelVersion {
  final String versionId;
  final int major;
  final int minor;
  final int patch;
  final DateTime createdAt;
  final String changelog;
  final String artifactHash;

  const ModelVersion({
    required this.versionId,
    required this.major,
    required this.minor,
    required this.patch,
    required this.createdAt,
    this.changelog = '',
    this.artifactHash = '',
  });

  String get semver => '$major.$minor.$patch';

  @override
  String toString() => 'v$semver ($versionId)';
}

class DeploymentInfo {
  final String environment;
  final String region;
  final int replicas;
  final String targetPlatform;
  final DateTime deployedAt;
  final double uptimeHours;

  const DeploymentInfo({
    required this.environment,
    required this.region,
    required this.replicas,
    required this.targetPlatform,
    required this.deployedAt,
    this.uptimeHours = 0,
  });
}

class OmniModelCard {
  final String modelId;
  final String name;
  final String description;
  final ModelStatus status;
  final ModelFramework framework;
  final ModelArchitecture architecture;
  final ModelMetrics metrics;
  final ModelVersion version;
  final DeploymentInfo? deployment;
  final List<String> tags;
  final String author;
  final String license;
  final DateTime createdAt;
  final DateTime updatedAt;

  const OmniModelCard({
    required this.modelId,
    required this.name,
    required this.description,
    required this.status,
    required this.framework,
    required this.architecture,
    required this.metrics,
    required this.version,
    this.deployment,
    this.tags = const [],
    this.author = '',
    this.license = 'MIT',
    required this.createdAt,
    required this.updatedAt,
  });

  bool get isDeployed => status == ModelStatus.deployed;
  bool get isMultimodal => architecture.modalities.length > 1;

  String get statusEmoji {
    switch (status) {
      case ModelStatus.training: return '🔄';
      case ModelStatus.validating: return '🔍';
      case ModelStatus.deployed: return '✅';
      case ModelStatus.archived: return '📦';
      case ModelStatus.failed: return '❌';
    }
  }

  double get qualityScore {
    final accuracyWeight = 0.4;
    final f1Weight = 0.3;
    final latencyWeight = 0.2;
    final sizeWeight = 0.1;

    final normalizedLatency = max(0.0, 1.0 - (metrics.latencyMs / 1000.0));
    final normalizedSize = max(0.0, 1.0 - (metrics.modelSizeMb / 10000.0));

    return (metrics.accuracy * accuracyWeight +
            metrics.f1Score * f1Weight +
            normalizedLatency * latencyWeight +
            normalizedSize * sizeWeight);
  }

  Map<String, dynamic> toJson() => {
    'model_id': modelId,
    'name': name,
    'description': description,
    'status': status.name,
    'framework': framework.name,
    'architecture': architecture.toJson(),
    'metrics': metrics.toJson(),
    'version': version.semver,
    'tags': tags,
    'author': author,
    'license': license,
    'quality_score': qualityScore,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };

  @override
  String toString() =>
    '$statusEmoji $name v${version.semver} | '
    '${metrics.formattedParams} params | '
    'acc=${(metrics.accuracy * 100).toStringAsFixed(1)}% | '
    '${metrics.latencyMs.toStringAsFixed(1)}ms';
}

class ModelCardRegistry {
  final Map<String, OmniModelCard> _cards = {};

  void register(OmniModelCard card) {
    _cards[card.modelId] = card;
  }

  OmniModelCard? get(String modelId) => _cards[modelId];

  List<OmniModelCard> search({
    String? query,
    ModelStatus? status,
    ModelFramework? framework,
    List<String>? tags,
  }) {
    return _cards.values.where((card) {
      if (query != null && !card.name.toLowerCase().contains(query.toLowerCase()) &&
          !card.description.toLowerCase().contains(query.toLowerCase())) {
        return false;
      }
      if (status != null && card.status != status) return false;
      if (framework != null && card.framework != framework) return false;
      if (tags != null && !tags.every((t) => card.tags.contains(t))) return false;
      return true;
    }).toList()
      ..sort((a, b) => b.qualityScore.compareTo(a.qualityScore));
  }

  List<OmniModelCard> get deployed =>
    _cards.values.where((c) => c.isDeployed).toList();

  int get count => _cards.length;
}
