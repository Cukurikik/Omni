// OMNI FRAMEWORK — UI LAYER: DART/FLUTTER CORE
// omni_animation_engine.dart — Declarative Animation System
// ==========================================================
// Production-grade animation engine for OMNI cross-platform UI.
// Implements deterministic timing functions, keyframe interpolation,
// and animation composition without simulation or random values.
//
// OMNI Layer: ui/dart_core
// @since 2026.4.2

import 'dart:math' as math;

// ---------------------------------------------------------------------------
// 1. MONADIC RESULT TYPE (OMNI STRICT RULE §3.1)
// ---------------------------------------------------------------------------

/// Typed error for animation operations.
class AnimError {
  final String code;
  final String message;
  const AnimError(this.code, this.message);

  @override
  String toString() => '[$code] $message';
}

/// Monadic Result type — replaces try/catch patterns.
sealed class Result<T> {
  const Result();
}

class Ok<T> extends Result<T> {
  final T value;
  const Ok(this.value);
}

class Err<T> extends Result<T> {
  final AnimError error;
  const Err(this.error);
}

/// Extension for Result chaining.
extension ResultOps<T> on Result<T> {
  bool get isOk => this is Ok<T>;

  T? get valueOrNull => switch (this) {
    Ok<T> ok => ok.value,
    Err<T> _ => null,
  };

  Result<U> map<U>(U Function(T) fn) => switch (this) {
    Ok<T> ok => Ok(fn(ok.value)),
    Err<T> err => Err(err.error),
  };

  Result<U> flatMap<U>(Result<U> Function(T) fn) => switch (this) {
    Ok<T> ok => fn(ok.value),
    Err<T> err => Err(err.error),
  };

  T unwrapOr(T fallback) => switch (this) {
    Ok<T> ok => ok.value,
    Err<T> _ => fallback,
  };
}

// ---------------------------------------------------------------------------
// 2. EASING FUNCTIONS (Pure Mathematical — No Simulation)
// ---------------------------------------------------------------------------

/// Standard easing functions implementing Robert Penner's equations.
/// All functions map t ∈ [0, 1] → value ∈ [0, 1].
class Easings {
  /// Linear interpolation (identity function).
  static double linear(double t) => t;

  /// Quadratic ease-in: f(t) = t²
  static double easeInQuad(double t) => t * t;

  /// Quadratic ease-out: f(t) = 1 - (1-t)²
  static double easeOutQuad(double t) => 1.0 - (1.0 - t) * (1.0 - t);

  /// Quadratic ease-in-out.
  static double easeInOutQuad(double t) =>
      t < 0.5 ? 2.0 * t * t : 1.0 - math.pow(-2.0 * t + 2.0, 2) / 2.0;

  /// Cubic ease-in: f(t) = t³
  static double easeInCubic(double t) => t * t * t;

  /// Cubic ease-out: f(t) = 1 - (1-t)³
  static double easeOutCubic(double t) =>
      1.0 - math.pow(1.0 - t, 3);

  /// Cubic ease-in-out.
  static double easeInOutCubic(double t) =>
      t < 0.5 ? 4.0 * t * t * t : 1.0 - math.pow(-2.0 * t + 2.0, 3) / 2.0;

  /// Elastic ease-out (spring-like bounce).
  static double easeOutElastic(double t) {
    if (t == 0.0 || t == 1.0) return t;
    const c4 = (2.0 * math.pi) / 3.0;
    return math.pow(2.0, -10.0 * t) * math.sin((t * 10.0 - 0.75) * c4) + 1.0;
  }

  /// Bounce ease-out.
  static double easeOutBounce(double t) {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1.0 / d1) {
      return n1 * t * t;
    } else if (t < 2.0 / d1) {
      final t2 = t - 1.5 / d1;
      return n1 * t2 * t2 + 0.75;
    } else if (t < 2.5 / d1) {
      final t2 = t - 2.25 / d1;
      return n1 * t2 * t2 + 0.9375;
    } else {
      final t2 = t - 2.625 / d1;
      return n1 * t2 * t2 + 0.984375;
    }
  }

  /// Cubic bezier easing (approximation via Newton-Raphson).
  /// Control points: (x1, y1), (x2, y2).
  static double cubicBezier(double t, double x1, double y1, double x2, double y2) {
    // Newton-Raphson to solve for parameter u where bezierX(u) = t
    double u = t; // initial guess
    for (int i = 0; i < 8; i++) {
      final bx = _bezier(u, x1, x2) - t;
      final dx = _bezierDerivative(u, x1, x2);
      if (dx.abs() < 1e-10) break;
      u -= bx / dx;
      u = u.clamp(0.0, 1.0);
    }
    return _bezier(u, y1, y2);
  }

  static double _bezier(double t, double p1, double p2) {
    final t2 = 1.0 - t;
    return 3.0 * t2 * t2 * t * p1 + 3.0 * t2 * t * t * p2 + t * t * t;
  }

  static double _bezierDerivative(double t, double p1, double p2) {
    final t2 = 1.0 - t;
    return 3.0 * t2 * t2 * p1 + 6.0 * t2 * t * (p2 - p1) + 3.0 * t * t * (1.0 - p2);
  }
}

// ---------------------------------------------------------------------------
// 3. KEYFRAME SYSTEM
// ---------------------------------------------------------------------------

/// A single keyframe at a specific time with a value and easing.
class Keyframe<T> {
  /// Time position in [0, 1] relative to animation duration.
  final double time;
  /// Value at this keyframe.
  final T value;
  /// Easing function used to interpolate TO this keyframe.
  final double Function(double) easing;

  const Keyframe({
    required this.time,
    required this.value,
    this.easing = Easings.linear,
  });
}

/// Interpolator function type for custom value types.
typedef Interpolator<T> = T Function(T a, T b, double t);

/// Keyframe track that interpolates between keyframes.
class KeyframeTrack<T> {
  final String name;
  final List<Keyframe<T>> keyframes;
  final Interpolator<T> interpolator;

  KeyframeTrack({
    required this.name,
    required this.keyframes,
    required this.interpolator,
  });

  /// Evaluates the track at time t ∈ [0, 1].
  ///
  /// Returns a Result containing the interpolated value.
  Result<T> evaluate(double t) {
    if (keyframes.isEmpty) {
      return Err(const AnimError('EMPTY_TRACK', 'No keyframes defined'));
    }
    if (t <= keyframes.first.time) return Ok(keyframes.first.value);
    if (t >= keyframes.last.time) return Ok(keyframes.last.value);

    // Find surrounding keyframes
    for (int i = 0; i < keyframes.length - 1; i++) {
      final kf0 = keyframes[i];
      final kf1 = keyframes[i + 1];
      if (t >= kf0.time && t <= kf1.time) {
        final segment = kf1.time - kf0.time;
        if (segment <= 0) return Ok(kf1.value);
        final localT = (t - kf0.time) / segment;
        final easedT = kf1.easing(localT);
        return Ok(interpolator(kf0.value, kf1.value, easedT));
      }
    }

    return Ok(keyframes.last.value);
  }
}

// ---------------------------------------------------------------------------
// 4. ANIMATION COMPOSITION
// ---------------------------------------------------------------------------

/// Animation status.
enum AnimStatus { idle, running, paused, completed }

/// A complete animation combining multiple tracks.
class Animation {
  final String id;
  final double durationMs;
  final bool loop;
  final List<KeyframeTrack<double>> tracks;
  AnimStatus _status;
  double _currentTime;
  int _loopCount;

  Animation({
    required this.id,
    required this.durationMs,
    this.loop = false,
    required this.tracks,
  })  : _status = AnimStatus.idle,
        _currentTime = 0,
        _loopCount = 0;

  AnimStatus get status => _status;
  double get currentTime => _currentTime;
  int get loopCount => _loopCount;

  /// Advances the animation by deltaMs milliseconds.
  ///
  /// Returns a Result containing a map of track name → current value.
  Result<Map<String, double>> advance(double deltaMs) {
    if (durationMs <= 0) {
      return Err(const AnimError('INVALID_DURATION', 'Duration must be > 0'));
    }

    _status = AnimStatus.running;
    _currentTime += deltaMs;

    if (_currentTime >= durationMs) {
      if (loop) {
        _loopCount++;
        _currentTime = _currentTime % durationMs;
      } else {
        _currentTime = durationMs;
        _status = AnimStatus.completed;
      }
    }

    final normalizedT = _currentTime / durationMs;
    final values = <String, double>{};

    for (final track in tracks) {
      final result = track.evaluate(normalizedT);
      switch (result) {
        case Ok<double> ok:
          values[track.name] = ok.value;
        case Err<double> err:
          return Err(err.error);
      }
    }

    return Ok(values);
  }

  /// Resets the animation to its initial state.
  void reset() {
    _currentTime = 0;
    _loopCount = 0;
    _status = AnimStatus.idle;
  }
}

// ---------------------------------------------------------------------------
// 5. ENGINE CLASS
// ---------------------------------------------------------------------------

/// Production-grade animation engine for OMNI UI layer.
class OmniAnimationEngine {
  static const String version = '1.1.0-omni-zeromock';
  static const String engineId = 'omni-animation-engine';

  final Map<String, Animation> _animations = {};

  /// Registers an animation.
  Result<String> register(Animation animation) {
    if (_animations.containsKey(animation.id)) {
      return Err(AnimError('DUPLICATE', 'Animation "${animation.id}" already registered'));
    }
    _animations[animation.id] = animation;
    return Ok(animation.id);
  }

  /// Advances a specific animation.
  Result<Map<String, double>> advance(String animationId, double deltaMs) {
    final anim = _animations[animationId];
    if (anim == null) {
      return Err(AnimError('NOT_FOUND', 'Animation "$animationId" not found'));
    }
    return anim.advance(deltaMs);
  }

  /// Resets a specific animation.
  Result<bool> resetAnimation(String animationId) {
    final anim = _animations[animationId];
    if (anim == null) {
      return Err(AnimError('NOT_FOUND', 'Animation "$animationId" not found'));
    }
    anim.reset();
    return const Ok(true);
  }

  /// Standard double interpolator (linear lerp).
  static double lerpDouble(double a, double b, double t) => a + (b - a) * t;

  /// Returns engine diagnostic information.
  Map<String, dynamic> diagnostics() => {
    'engine': engineId,
    'version': version,
    'layer': 'ui/dart_core',
    'registeredAnimations': _animations.length,
    'animations': _animations.entries.map((e) => {
      'id': e.key,
      'status': e.value.status.name,
      'durationMs': e.value.durationMs,
      'tracks': e.value.tracks.length,
      'loopCount': e.value.loopCount,
    }).toList(),
    'easings': [
      'linear', 'easeInQuad', 'easeOutQuad', 'easeInOutQuad',
      'easeInCubic', 'easeOutCubic', 'easeInOutCubic',
      'easeOutElastic', 'easeOutBounce', 'cubicBezier',
    ],
    'mockPatterns': 'zero',
  };
}
