class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class SamplingViewerUI {
  OmniResult<bool> updatePreview(List<int> imageBytes, int currentStep) {
    if (imageBytes.isEmpty || currentStep < 0) {
      return OmniResult(error: 'Invalid preview data');
    }

    // Dart frontend logic for visualizing VQ-DDPM sampling steps live
    print('Updated preview at step $currentStep');
    
    return OmniResult(value: true);
  }
}
