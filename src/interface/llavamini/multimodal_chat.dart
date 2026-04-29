class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class MultimodalChat {
  OmniResult<bool> sendMessage(String text, List<int> imageBytes) {
    if (text.isEmpty && imageBytes.isEmpty) {
      return OmniResult(error: 'Cannot send empty message');
    }

    // Dart frontend logic for LLaVA-Mini multimodal chat UI
    print('Sending multimodal message. Text length: ${text.length}, Image size: ${imageBytes.length}');
    
    return OmniResult(value: true);
  }
}
