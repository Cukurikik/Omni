class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class TrainingMonitorUI {
  OmniResult<bool> displayCacheStats(int memUsed, int memSaved) {
    if (memUsed < 0 || memSaved < 0) {
      return OmniResult(error: 'Invalid memory stats');
    }

    // Dart frontend logic for visualizing GradCache memory savings
    print('GradCache Memory Used: \$memUsed MB | Saved: \$memSaved MB');
    
    return OmniResult(value: true);
  }
}
