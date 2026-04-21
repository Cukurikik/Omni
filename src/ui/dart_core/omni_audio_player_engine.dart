// ===========================================================================
// OMNI AUDIO PLAYER ENGINE (POLYLINGUAL REMEDIATION)
// ===========================================================================
// Absorbed From  : audioplayers + media_kit Flutter concepts
// Logic Inherited: Dart / UI Layer (StreamController Cross-Platform Playback)
// Domain Layer   : UI Mobile (Dart Core)
// ===========================================================================
//
// By studying the audioplayers and media_kit Flutter packages, Mother
// learned that cross-platform audio playback on mobile/desktop requires:
//   1. Stream-based state management (Dart StreamController)
//   2. Platform lifecycle awareness (pause on backgrounding)
//   3. Audio focus management (duck other apps)
//   4. Mixins for composable behavior (equalization, looping)
//
// Dart's StreamController + async/await is the native reactive primitive
// for Flutter—no third-party state management library needed.

import 'dart:async';
import 'dart:math';

// ---- Enums ----

enum AudioPlayerState {
  idle,
  loading,
  ready,
  playing,
  paused,
  stopped,
  completed,
  error,
}

enum AudioFocusMode {
  gain,          // Full audio focus
  gainTransient, // Short-term focus (notification)
  duck,          // Lower other audio, don't stop
  abandon,       // Release focus
}

enum LoopMode {
  off,
  one,
  all,
}

// ---- Data Models ----

class AudioSource {
  final String uri;
  final String title;
  final String artist;
  final Duration? duration;
  final Map<String, dynamic> metadata;

  AudioSource({
    required this.uri,
    this.title = 'Unknown',
    this.artist = 'Unknown',
    this.duration,
    this.metadata = const {},
  });

  bool get isLocal => uri.startsWith('file://') || uri.startsWith('/');
  bool get isNetwork => uri.startsWith('http://') || uri.startsWith('https://');

  @override
  String toString() => 'AudioSource($title - $artist)';
}

class AudioPosition {
  final Duration current;
  final Duration total;
  final Duration buffered;

  AudioPosition({
    required this.current,
    required this.total,
    this.buffered = Duration.zero,
  });

  double get progress => total.inMilliseconds > 0
      ? current.inMilliseconds / total.inMilliseconds
      : 0.0;

  double get bufferProgress => total.inMilliseconds > 0
      ? buffered.inMilliseconds / total.inMilliseconds
      : 0.0;
}

class PlayerError {
  final String code;
  final String message;
  final DateTime timestamp;

  PlayerError({
    required this.code,
    required this.message,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

// ---- Equalizer Mixin ----

mixin EqualizerMixin {
  final Map<int, double> _bands = {};

  static const List<int> standardBands = [
    60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000,
  ];

  void setBandGain(int frequencyHz, double gainDb) {
    final clampedGain = gainDb.clamp(-12.0, 12.0);
    _bands[frequencyHz] = clampedGain;
  }

  double getBandGain(int frequencyHz) => _bands[frequencyHz] ?? 0.0;

  Map<int, double> getAllBands() => Map.unmodifiable(_bands);

  void resetEqualizer() => _bands.clear();

  void applyPreset(String preset) {
    resetEqualizer();
    switch (preset) {
      case 'bass_boost':
        setBandGain(60, 6.0);
        setBandGain(170, 4.0);
        setBandGain(310, 2.0);
        break;
      case 'vocal':
        setBandGain(310, 3.0);
        setBandGain(600, 4.0);
        setBandGain(1000, 4.0);
        setBandGain(3000, 2.0);
        break;
      case 'treble_boost':
        setBandGain(6000, 3.0);
        setBandGain(12000, 4.0);
        setBandGain(14000, 5.0);
        setBandGain(16000, 4.0);
        break;
      default:
        break;
    }
  }
}

// ---- Playlist Mixin ----

mixin PlaylistMixin {
  final List<AudioSource> _playlist = [];
  int _currentIndex = -1;
  LoopMode _loopMode = LoopMode.off;
  bool _shuffle = false;
  final List<int> _shuffleOrder = [];
  final Random _rng = Random();

  void addToPlaylist(AudioSource source) {
    _playlist.add(source);
    _regenerateShuffleOrder();
  }

  void removeFromPlaylist(int index) {
    if (index >= 0 && index < _playlist.length) {
      _playlist.removeAt(index);
      _regenerateShuffleOrder();
      if (_currentIndex >= _playlist.length) {
        _currentIndex = _playlist.length - 1;
      }
    }
  }

  void clearPlaylist() {
    _playlist.clear();
    _currentIndex = -1;
    _shuffleOrder.clear();
  }

  AudioSource? get currentTrack =>
      (_currentIndex >= 0 && _currentIndex < _playlist.length)
          ? _playlist[_currentIndex]
          : null;

  int get playlistLength => _playlist.length;
  int get currentIndex => _currentIndex;

  AudioSource? nextTrack() {
    if (_playlist.isEmpty) return null;

    if (_shuffle) {
      final shuffleIdx = _shuffleOrder.indexOf(_currentIndex);
      if (shuffleIdx + 1 < _shuffleOrder.length) {
        _currentIndex = _shuffleOrder[shuffleIdx + 1];
      } else if (_loopMode == LoopMode.all) {
        _regenerateShuffleOrder();
        _currentIndex = _shuffleOrder.first;
      } else {
        return null;
      }
    } else {
      if (_currentIndex + 1 < _playlist.length) {
        _currentIndex++;
      } else if (_loopMode == LoopMode.all) {
        _currentIndex = 0;
      } else {
        return null;
      }
    }
    return currentTrack;
  }

  AudioSource? previousTrack() {
    if (_playlist.isEmpty) return null;
    if (_currentIndex > 0) {
      _currentIndex--;
    } else if (_loopMode == LoopMode.all) {
      _currentIndex = _playlist.length - 1;
    }
    return currentTrack;
  }

  void setLoopMode(LoopMode mode) => _loopMode = mode;
  void setShuffle(bool enabled) {
    _shuffle = enabled;
    if (enabled) _regenerateShuffleOrder();
  }

  void _regenerateShuffleOrder() {
    _shuffleOrder
      ..clear()
      ..addAll(List.generate(_playlist.length, (i) => i))
      ..shuffle(_rng);
  }
}

// ---- Core Engine ----

class OmniAudioPlayerEngine with EqualizerMixin, PlaylistMixin {
  // Stream controllers for reactive state
  final StreamController<AudioPlayerState> _stateController =
      StreamController<AudioPlayerState>.broadcast();
  final StreamController<AudioPosition> _positionController =
      StreamController<AudioPosition>.broadcast();
  final StreamController<PlayerError> _errorController =
      StreamController<PlayerError>.broadcast();
  final StreamController<double> _volumeController =
      StreamController<double>.broadcast();

  AudioPlayerState _state = AudioPlayerState.idle;
  double _volume = 1.0;
  double _speed = 1.0;
  AudioFocusMode _focusMode = AudioFocusMode.gain;

  Timer? _positionTimer;
  Duration _currentPosition = Duration.zero;
  Duration _totalDuration = Duration.zero;

  // --- Public Streams ---

  Stream<AudioPlayerState> get stateStream => _stateController.stream;
  Stream<AudioPosition> get positionStream => _positionController.stream;
  Stream<PlayerError> get errorStream => _errorController.stream;
  Stream<double> get volumeStream => _volumeController.stream;

  AudioPlayerState get state => _state;
  double get volume => _volume;
  double get speed => _speed;

  // --- Lifecycle ---

  Future<void> load(AudioSource source) async {
    _setState(AudioPlayerState.loading);
    addToPlaylist(source);
    _currentIndex = _playlist.length - 1;

    // Simulate async load (in production: platform channel to native player)
    await Future.delayed(const Duration(milliseconds: 50));
    _totalDuration = source.duration ?? const Duration(minutes: 3);
    _currentPosition = Duration.zero;
    _setState(AudioPlayerState.ready);
  }

  Future<void> play() async {
    if (_state == AudioPlayerState.ready || _state == AudioPlayerState.paused) {
      _setState(AudioPlayerState.playing);
      _startPositionUpdates();
    }
  }

  Future<void> pause() async {
    if (_state == AudioPlayerState.playing) {
      _stopPositionUpdates();
      _setState(AudioPlayerState.paused);
    }
  }

  Future<void> stop() async {
    _stopPositionUpdates();
    _currentPosition = Duration.zero;
    _setState(AudioPlayerState.stopped);
  }

  Future<void> seekTo(Duration position) async {
    _currentPosition = Duration(
      milliseconds: position.inMilliseconds.clamp(0, _totalDuration.inMilliseconds),
    );
    _emitPosition();
  }

  Future<void> skipNext() async {
    final next = nextTrack();
    if (next != null) {
      _stopPositionUpdates();
      await load(next);
      await play();
    }
  }

  Future<void> skipPrevious() async {
    // If more than 3 seconds in, restart; otherwise go previous
    if (_currentPosition.inSeconds > 3) {
      await seekTo(Duration.zero);
      return;
    }
    final prev = previousTrack();
    if (prev != null) {
      _stopPositionUpdates();
      await load(prev);
      await play();
    }
  }

  void setVolume(double vol) {
    _volume = vol.clamp(0.0, 1.0);
    _volumeController.add(_volume);
  }

  void setSpeed(double rate) {
    _speed = rate.clamp(0.25, 4.0);
  }

  void setAudioFocus(AudioFocusMode mode) {
    _focusMode = mode;
  }

  // --- Lifecycle Management ---

  void onAppPaused() {
    // Auto-pause when app goes to background (mobile best practice)
    if (_state == AudioPlayerState.playing) {
      pause();
    }
  }

  void onAppResumed() {
    // Don't auto-resume — let user decide
  }

  // --- Cleanup ---

  Future<void> dispose() async {
    _stopPositionUpdates();
    await _stateController.close();
    await _positionController.close();
    await _errorController.close();
    await _volumeController.close();
  }

  // --- Private ---

  void _setState(AudioPlayerState newState) {
    _state = newState;
    if (!_stateController.isClosed) {
      _stateController.add(newState);
    }
  }

  void _startPositionUpdates() {
    _stopPositionUpdates();
    _positionTimer = Timer.periodic(const Duration(milliseconds: 250), (_) {
      if (_state == AudioPlayerState.playing) {
        _currentPosition += Duration(milliseconds: (250 * _speed).round());

        if (_currentPosition >= _totalDuration) {
          // Track completed
          _stopPositionUpdates();
          if (_loopMode == LoopMode.one) {
            _currentPosition = Duration.zero;
            _startPositionUpdates();
          } else {
            _setState(AudioPlayerState.completed);
            // Auto-advance playlist
            final next = nextTrack();
            if (next != null) {
              load(next).then((_) => play());
            }
          }
        } else {
          _emitPosition();
        }
      }
    });
  }

  void _stopPositionUpdates() {
    _positionTimer?.cancel();
    _positionTimer = null;
  }

  void _emitPosition() {
    if (!_positionController.isClosed) {
      _positionController.add(AudioPosition(
        current: _currentPosition,
        total: _totalDuration,
        buffered: _totalDuration, // Simulated: fully buffered
      ));
    }
  }

  // --- Diagnostics ---

  Map<String, dynamic> diagnostics() {
    return {
      'engine': 'OmniAudioPlayerEngine',
      'layer': 'Dart UI Mobile',
      'state': _state.name,
      'volume': _volume,
      'speed': _speed,
      'loop_mode': _loopMode.name,
      'shuffle': _shuffle,
      'playlist_length': _playlist.length,
      'current_index': _currentIndex,
      'current_track': currentTrack?.toString(),
      'position_ms': _currentPosition.inMilliseconds,
      'duration_ms': _totalDuration.inMilliseconds,
      'progress': (_totalDuration.inMilliseconds > 0)
          ? (_currentPosition.inMilliseconds / _totalDuration.inMilliseconds)
          : 0.0,
      'eq_bands': getAllBands().length,
      'focus_mode': _focusMode.name,
      'learned_logic': [
        'stream-controller-broadcast-reactive',
        'mixin-based-composable-behavior',
        'playlist-shuffle-fisher-yates',
        'timer-periodic-position-simulation',
        'audio-focus-lifecycle-management',
        'equalizer-preset-band-system',
        'loop-mode-finite-state-machine',
      ],
    };
  }
}
