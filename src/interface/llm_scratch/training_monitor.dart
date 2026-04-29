class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class TrainingMonitorUI {
  OmniResult<bool> updateLoss(double currentLoss) {
    if (currentLoss.isNaN) {
      return OmniResult(error: 'NaN loss detected');
    }

    // Dart frontend logic for visualizing from-scratch LLM training curves
    print('Current training loss: $currentLoss');
    
    return OmniResult(value: true);
  }
}
