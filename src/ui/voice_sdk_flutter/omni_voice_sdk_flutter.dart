/// OMNI Voice SDK Flutter — Interface Layer
/// Absorbing alan-ai/alan-sdk-flutter voice assistant integration patterns.
/// Dart-idiomatic sealed class for voice session management.

class VoiceFlutterResult<T> {
  final bool ok;
  final T? data;
  final String? error;
  VoiceFlutterResult.success(this.data) : ok = true, error = null;
  VoiceFlutterResult.failure(this.error) : ok = false, data = null;
}

class VoiceSession {
  final String sessionId;
  final DateTime startedAt;
  bool isActive;
  int commandCount;

  VoiceSession(this.sessionId)
      : startedAt = DateTime.now(),
        isActive = true,
        commandCount = 0;
}

class OmniVoiceSdkFlutterEngine {
  final Map<String, VoiceSession> _sessions = {};
  final Map<String, Function> _handlers = {};
  int _totalCommands = 0;

  VoiceFlutterResult<String> startSession(String sessionId) {
    if (sessionId.isEmpty) {
      return VoiceFlutterResult.failure('VoiceFlutterError: Empty session ID');
    }
    if (_sessions.containsKey(sessionId)) {
      return VoiceFlutterResult.failure('VoiceFlutterError: Session exists');
    }
    _sessions[sessionId] = VoiceSession(sessionId);
    return VoiceFlutterResult.success(sessionId);
  }

  VoiceFlutterResult<bool> registerHandler(String intent, Function handler) {
    if (intent.isEmpty) {
      return VoiceFlutterResult.failure('VoiceFlutterError: Empty intent');
    }
    _handlers[intent] = handler;
    return VoiceFlutterResult.success(true);
  }

  VoiceFlutterResult<dynamic> processVoice(String sessionId, String intent, Map<String, dynamic> payload) {
    if (!_sessions.containsKey(sessionId)) {
      return VoiceFlutterResult.failure('VoiceFlutterError: Session not found');
    }
    final session = _sessions[sessionId]!;
    if (!session.isActive) {
      return VoiceFlutterResult.failure('VoiceFlutterError: Session ended');
    }
    if (!_handlers.containsKey(intent)) {
      return VoiceFlutterResult.failure('VoiceFlutterError: No handler for "$intent"');
    }
    session.commandCount++;
    _totalCommands++;
    try {
      final result = _handlers[intent]!(payload);
      return VoiceFlutterResult.success(result);
    } catch (e) {
      return VoiceFlutterResult.failure('VoiceFlutterError: $e');
    }
  }

  VoiceFlutterResult<bool> endSession(String sessionId) {
    if (!_sessions.containsKey(sessionId)) {
      return VoiceFlutterResult.failure('VoiceFlutterError: Session not found');
    }
    _sessions[sessionId]!.isActive = false;
    return VoiceFlutterResult.success(true);
  }

  Map<String, dynamic> diagnostics() => {
    'engine': 'OmniVoiceSdkFlutterEngine',
    'sessions': _sessions.length,
    'handlers': _handlers.length,
    'totalCommands': _totalCommands,
    'status': 'Operational',
  };
}
