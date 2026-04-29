class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class ChatUI {
  OmniResult<bool> renderMessage(String role, String content) {
    if (content.isEmpty) {
      return OmniResult(error: 'Empty message content');
    }

    // Dart frontend logic for MiniMax chat UI rendering
    print('Rendering message from $role: $content');
    
    return OmniResult(value: true);
  }
}
