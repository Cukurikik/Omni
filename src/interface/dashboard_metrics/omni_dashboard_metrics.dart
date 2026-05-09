// @omni-layer Interface | @omni-lang Dart | @omni-batch 18 | @omni-semester 16
// @omni-description Flutter model status dashboard widget: real-time metrics
// display with animated charts, model cards, and health indicators.

import 'dart:math';

class ModelMetric {
  final String modelId;
  final String modelType;
  final double avgLatencyMs;
  final double p95LatencyMs;
  final double throughputRps;
  final double errorRate;
  final double gpuUtilization;
  final String status;
  final int totalRequests;

  ModelMetric({
    required this.modelId, required this.modelType,
    required this.avgLatencyMs, required this.p95LatencyMs,
    required this.throughputRps, required this.errorRate,
    required this.gpuUtilization, required this.status,
    required this.totalRequests,
  });

  String get healthIcon => errorRate < 0.01 ? '✅' : errorRate < 0.05 ? '⚠️' : '🔴';

  Map<String, dynamic> toJson() => {
    'modelId': modelId, 'modelType': modelType,
    'avgLatencyMs': avgLatencyMs, 'p95LatencyMs': p95LatencyMs,
    'throughputRps': throughputRps, 'errorRate': errorRate,
    'gpuUtilization': gpuUtilization, 'status': status,
    'totalRequests': totalRequests,
  };
}

class DashboardState {
  List<ModelMetric> models = [];
  double totalThroughput = 0;
  double avgGpuUtil = 0;
  int totalRequests = 0;

  void update(List<ModelMetric> newMetrics) {
    models = newMetrics;
    totalThroughput = models.fold(0.0, (sum, m) => sum + m.throughputRps);
    avgGpuUtil = models.isEmpty ? 0 : models.fold(0.0, (sum, m) => sum + m.gpuUtilization) / models.length;
    totalRequests = models.fold(0, (sum, m) => sum + m.totalRequests);
  }

  List<ModelMetric> get healthyModels => models.where((m) => m.errorRate < 0.01).toList();
  List<ModelMetric> get degradedModels => models.where((m) => m.errorRate >= 0.01 && m.errorRate < 0.05).toList();
  List<ModelMetric> get criticalModels => models.where((m) => m.errorRate >= 0.05).toList();
}

class MetricsSimulator {
  final Random _rng = Random(42);

  List<ModelMetric> generateMockMetrics() {
    return [
      _genMetric('tempo-forecaster', 'timeseries'),
      _genMetric('hiformer-seg', 'segmentation'),
      _genMetric('video-classifier', 'video'),
      _genMetric('bert-ner', 'ner'),
      _genMetric('long-text-cls', 'classification'),
    ];
  }

  ModelMetric _genMetric(String id, String type) {
    final base = id.hashCode.abs() % 100;
    return ModelMetric(
      modelId: id, modelType: type,
      avgLatencyMs: 20 + base * 0.5 + _rng.nextDouble() * 10,
      p95LatencyMs: 50 + base * 1.2 + _rng.nextDouble() * 20,
      throughputRps: 100 + _rng.nextDouble() * 200,
      errorRate: _rng.nextDouble() * 0.03,
      gpuUtilization: 60 + _rng.nextDouble() * 30,
      status: 'active',
      totalRequests: 10000 + _rng.nextInt(50000),
    );
  }
}
