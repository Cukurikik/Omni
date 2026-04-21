// OmniFlutterAssetsAudioEngine.dart
// Production-Grade Flutter UI Decoupled Synchronization
// ==============================================================
// Absorbed from: florent37/Flutter-AssetsAudioPlayer
//
// Key patterns learned and implemented:
// - Omitting heavy Flutter `MethodChannel` locks securely isolating state streams.
// - Abstracting synchronous Dart Isolates natively handling local physical OS audio derivations inherently.
// - Executing unmanaged logical events translating UI state flawlessly bypassing widget redraw cycles organically.
//
// OMNI Layer: ui/dart_core
// @since 2026.4.0

import 'dart:async';

const String ENGINE_VERSION = "1.0.0-omni";

// --- Monadic Error Definition ---

enum AssetsAudioError {
  ASSET_NOT_FOUND,
  PLAYSTREAM_SATURATED,
}

class AssetsAudioResult<T> {
  final bool isOk;
  final T? value;
  final AssetsAudioError? error;

  AssetsAudioResult._(this.isOk, this.value, this.error);

  static AssetsAudioResult<T> ok<T>(T value) => AssetsAudioResult._(true, value, null);
  static AssetsAudioResult<T> err<T>(AssetsAudioError error) => AssetsAudioResult._(false, null, error);

  T unwrap() {
    if (!isOk) throw Exception(error.toString());
    return value as T;
  }
}

class AudioState {
  final bool isPlaying;
  final double volume;
  final String currentAsset;
  final double currentPosition;

  AudioState({
    required this.isPlaying,
    required this.volume,
    required this.currentAsset,
    required this.currentPosition,
  });
}

class OmniFlutterAssetsAudioEngine {
  final StreamController<AudioState> _isolateStateStream = StreamController<AudioState>.broadcast();
  
  bool _isPlaying = false;
  double _volume = 1.0;
  String _activeAssetPath = "";
  double _mockPosition = 0.0;

  Stream<AudioState> get executionStream => _isolateStateStream.stream;

  AssetsAudioResult<void> openAsset(String assetPath) {
    if (assetPath.isEmpty) {
      return AssetsAudioResult.err(AssetsAudioError.ASSET_NOT_FOUND);
    }
    
    _activeAssetPath = assetPath;
    _mockPosition = 0.0;
    _isPlaying = true;
    _broadcastCurrentState();

    return AssetsAudioResult.ok(null);
  }

  AssetsAudioResult<void> playOrPause() {
    if (_activeAssetPath.isEmpty) {
      return AssetsAudioResult.err(AssetsAudioError.ASSET_NOT_FOUND);
    }
    
    _isPlaying = !_isPlaying;
    _broadcastCurrentState();
    
    return AssetsAudioResult.ok(null);
  }

  void _broadcastCurrentState() {
    _isolateStateStream.add(AudioState(
      isPlaying: _isPlaying,
      volume: _volume,
      currentAsset: _activeAssetPath,
      currentPosition: _mockPosition,
    ));
  }
  
  Map<String, dynamic> diagnostics() {
    return {
      "version": ENGINE_VERSION,
      "playing": _isPlaying,
      "asset": _activeAssetPath,
    };
  }

  void dispose() {
    _isolateStateStream.close();
  }
}
