class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class AudioTranscriptionUI {
  OmniResult<bool> displayTranscript(String text) {
    if (text.isEmpty) {
      return OmniResult(error: 'Empty transcript');
    }

    // Dart frontend logic for displaying live transcriptions (LTU)
    print('Transcript: $text');
    
    return OmniResult(value: true);
  }
}
