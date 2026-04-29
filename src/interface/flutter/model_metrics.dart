class ModelMetrics {
  final String modelId;
  final double accuracy;
  final double p99Latency;

  ModelMetrics({required this.modelId, required this.accuracy, required this.p99Latency});

  factory ModelMetrics.fromJson(Map<String, dynamic> json) {
    return ModelMetrics(
      modelId: json['modelId'],
      accuracy: json['accuracy'],
      p99Latency: json['p99Latency'],
    );
  }
}
