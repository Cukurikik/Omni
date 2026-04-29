class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class MultimodalChatUI {
  OmniResult<bool> displayMessage(String text, String? imageUrl) {
    if (text.isEmpty && imageUrl == null) {
      return OmniResult(error: 'Empty message');
    }

    // Dart frontend logic for fromage interleaved image-text chat
    print('Displaying: $text');
    if (imageUrl != null) print('Image: $imageUrl');
    
    return OmniResult(value: true);
  }
}
