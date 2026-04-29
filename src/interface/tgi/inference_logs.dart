class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class InferenceLogsUI {
  OmniResult<bool> displayLog(String message, String level) {
    if (message.isEmpty) {
      return OmniResult(error: 'Empty log message');
    }

    // Dart frontend logic for TGI real-time inference logging
    print('[$level] TGI: $message');
    
    return OmniResult(value: true);
  }
}
