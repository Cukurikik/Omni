// @omni-domain Interface Layer (MusicGen)
// @omni-source various/musicgen
// @omni-description MusicGen Player mimicking Dart audio rendering UI.
// @omni-requirement zero-mock, monadic-error

class OmniResult<T> {
  final bool ok;
  final T? value;
  final Exception? error;

  OmniResult.ok(this.value) : ok = true, error = null;
  OmniResult.err(this.error) : ok = false, value = null;
}

class Track {
  final String title;
  final String url;
  final double duration;

  Track(this.title, this.url, this.duration);
}

class MusicGenPlayer {
  Track? _currentTrack;
  bool _isPlaying = false;

  OmniResult<bool> loadTrack(String title, String url, double duration) {
    if (url.isEmpty || title.isEmpty) {
      return OmniResult.err(Exception("Track title and URL cannot be empty"));
    }
    _currentTrack = Track(title, url, duration);
    _isPlaying = false;
    return OmniResult.ok(true);
  }

  OmniResult<String> play() {
    if (_currentTrack == null) {
      return OmniResult.err(Exception("No track loaded"));
    }
    _isPlaying = true;
    return OmniResult.ok("Playing: ${_currentTrack!.title}");
  }

  OmniResult<String> stop() {
    if (_currentTrack == null) {
      return OmniResult.err(Exception("No track loaded"));
    }
    _isPlaying = false;
    return OmniResult.ok("Stopped: ${_currentTrack!.title}");
  }
}
