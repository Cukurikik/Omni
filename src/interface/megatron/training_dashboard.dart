class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class TrainingDashboard {
  OmniResult<bool> updateMetrics(double loss, int throughput) {
    if (loss < 0 || throughput < 0) {
      return OmniResult(error: 'Invalid metrics');
    }

    // Dart frontend logic for Megatron training visualization
    print('Updating dashboard: Loss=$loss, Throughput=$throughput TFLOPs');
    
    return OmniResult(value: true);
  }
}
