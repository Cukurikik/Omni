class OmniResult<T> {
  final T? value;
  final String? error;
  bool get isOk => error == null;

  OmniResult(this.value, this.error);
}

class TraceOptimizationUI {
  OmniResult<bool> renderLatencyGraph(List<double> latencies) {
    if (latencies.isEmpty) {
      return OmniResult(null, "No latency data to render");
    }

    // Flutter/Dart UI rendering simulation
    print("Rendering Trace Optimization Graph with \${latencies.length} data points.");
    
    return OmniResult(true, null);
  }
}
