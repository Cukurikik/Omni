// ===========================================================================
// OMNI STREAM ENGINE (SEMESTER 3 — BATCH 38.8)
// ===========================================================================
// Absorbed From  : Dart Streams + StreamController + RxDart
// Logic Inherited: Dart / Interface Layer (Reactive Stream Processing)
// ===========================================================================
//
// By studying Dart Streams and RxDart, Mother learned:
//   1. Stream = async sequence of events (single/broadcast)
//   2. StreamController bridges imperative → reactive
//   3. StreamTransformer enables custom operator chains
//   4. Broadcast streams allow multiple listeners
//   5. async* generators yield values into streams

import 'dart:async';

// ============================================================
// PART 1: Enhanced Stream Controller
// ============================================================

/// OmniStreamController: enhanced StreamController with metrics.
class OmniStreamController<T> {
  late final StreamController<T> _controller;
  int _totalAdded = 0;
  int _totalListeners = 0;
  int _totalErrors = 0;
  bool _isClosed = false;

  OmniStreamController({bool broadcast = false}) {
    if (broadcast) {
      _controller = StreamController<T>.broadcast(
        onListen: () => _totalListeners++,
      );
    } else {
      _controller = StreamController<T>(
        onListen: () => _totalListeners++,
      );
    }
  }

  /// Add a value to the stream.
  void add(T value) {
    if (_isClosed) throw StateError('Cannot add to closed stream');
    _totalAdded++;
    _controller.add(value);
  }

  /// Add an error to the stream.
  void addError(Object error, [StackTrace? stackTrace]) {
    _totalErrors++;
    _controller.addError(error, stackTrace);
  }

  /// Close the stream.
  Future<void> close() async {
    _isClosed = true;
    await _controller.close();
  }

  /// The stream to listen to.
  Stream<T> get stream => _controller.stream;

  /// The sink for adding values.
  StreamSink<T> get sink => _controller.sink;

  bool get isClosed => _isClosed;

  Map<String, dynamic> get stats => {
    'totalAdded': _totalAdded,
    'totalListeners': _totalListeners,
    'totalErrors': _totalErrors,
    'isClosed': _isClosed,
  };
}

// ============================================================
// PART 2: Stream Combinators (RxDart-inspired)
// ============================================================

/// Extension methods on Stream for RxDart-style operations.
extension OmniStreamExtensions<T> on Stream<T> {

  /// Debounce: emit only after a quiet period.
  Stream<T> debounceTime(Duration duration) {
    Timer? timer;
    late StreamController<T> controller;

    controller = StreamController<T>(
      onCancel: () => timer?.cancel(),
    );

    listen(
      (data) {
        timer?.cancel();
        timer = Timer(duration, () => controller.add(data));
      },
      onError: controller.addError,
      onDone: () {
        timer?.cancel();
        controller.close();
      },
    );

    return controller.stream;
  }

  /// Throttle: emit at most once per duration.
  Stream<T> throttleTime(Duration duration) {
    DateTime? lastEmit;
    late StreamController<T> controller;

    controller = StreamController<T>();

    listen(
      (data) {
        final now = DateTime.now();
        if (lastEmit == null || now.difference(lastEmit!) >= duration) {
          lastEmit = now;
          controller.add(data);
        }
      },
      onError: controller.addError,
      onDone: controller.close,
    );

    return controller.stream;
  }

  /// Buffer: collect N items then emit as list.
  Stream<List<T>> bufferCount(int count) {
    final buffer = <T>[];
    late StreamController<List<T>> controller;

    controller = StreamController<List<T>>();

    listen(
      (data) {
        buffer.add(data);
        if (buffer.length >= count) {
          controller.add(List<T>.from(buffer));
          buffer.clear();
        }
      },
      onError: controller.addError,
      onDone: () {
        if (buffer.isNotEmpty) controller.add(List<T>.from(buffer));
        controller.close();
      },
    );

    return controller.stream;
  }

  /// Scan: accumulate values over time.
  Stream<R> scan<R>(R initial, R Function(R accumulator, T value) combine) {
    var accumulator = initial;
    return map((value) {
      accumulator = combine(accumulator, value);
      return accumulator;
    });
  }

  /// Pairwise: emit previous and current value.
  Stream<List<T>> pairwise() {
    T? previous;
    bool hasPrevious = false;
    late StreamController<List<T>> controller;

    controller = StreamController<List<T>>();

    listen(
      (data) {
        if (hasPrevious) {
          controller.add([previous as T, data]);
        }
        previous = data;
        hasPrevious = true;
      },
      onError: controller.addError,
      onDone: controller.close,
    );

    return controller.stream;
  }

  /// Retry: re-subscribe on error.
  Stream<T> retryStream(int maxRetries) {
    var attempts = 0;
    late StreamController<T> controller;

    void subscribe() {
      listen(
        controller.add,
        onError: (error) {
          attempts++;
          if (attempts <= maxRetries) {
            subscribe();
          } else {
            controller.addError(error);
            controller.close();
          }
        },
        onDone: controller.close,
      );
    }

    controller = StreamController<T>(onListen: subscribe);
    return controller.stream;
  }

  /// StartWith: prepend a value before the stream.
  Stream<T> startWith(T value) async* {
    yield value;
    await for (final item in this) {
      yield item;
    }
  }

  /// SwitchMap: cancel previous inner stream on new emission.
  Stream<R> switchMap<R>(Stream<R> Function(T value) mapper) {
    StreamSubscription<R>? innerSub;
    late StreamController<R> controller;

    controller = StreamController<R>(
      onCancel: () => innerSub?.cancel(),
    );

    listen(
      (data) {
        innerSub?.cancel();
        innerSub = mapper(data).listen(
          controller.add,
          onError: controller.addError,
        );
      },
      onError: controller.addError,
      onDone: () async {
        await innerSub?.cancel();
        controller.close();
      },
    );

    return controller.stream;
  }
}

// ============================================================
// PART 3: Merge / CombineLatest (Static Combinators)
// ============================================================

/// Merge multiple streams into one.
Stream<T> mergeStreams<T>(List<Stream<T>> streams) {
  final controller = StreamController<T>.broadcast();
  var completedCount = 0;

  for (final stream in streams) {
    stream.listen(
      controller.add,
      onError: controller.addError,
      onDone: () {
        completedCount++;
        if (completedCount == streams.length) {
          controller.close();
        }
      },
    );
  }

  return controller.stream;
}

/// CombineLatest: emit when any source emits, combining latest values.
Stream<List<T>> combineLatest<T>(List<Stream<T>> streams) {
  final controller = StreamController<List<T>>.broadcast();
  final latestValues = List<T?>.filled(streams.length, null);
  final hasValue = List<bool>.filled(streams.length, false);
  var completedCount = 0;

  for (var i = 0; i < streams.length; i++) {
    streams[i].listen(
      (value) {
        latestValues[i] = value;
        hasValue[i] = true;
        if (hasValue.every((v) => v)) {
          controller.add(List<T>.from(latestValues.cast<T>()));
        }
      },
      onError: controller.addError,
      onDone: () {
        completedCount++;
        if (completedCount == streams.length) controller.close();
      },
    );
  }

  return controller.stream;
}

// ============================================================
// PART 4: Async Generator Utilities
// ============================================================

/// Generate a stream from an iterable with delay.
Stream<T> fromIterableDelayed<T>(Iterable<T> items, Duration delay) async* {
  for (final item in items) {
    await Future.delayed(delay);
    yield item;
  }
}

/// Generate a periodic counter stream.
Stream<int> periodicCounter({
  required Duration interval,
  int? maxCount,
}) async* {
  var count = 0;
  while (maxCount == null || count < maxCount) {
    await Future.delayed(interval);
    yield count;
    count++;
  }
}

// ============================================================
// Diagnostics
// ============================================================

Map<String, dynamic> streamDiagnostics() {
  return {
    'engine': 'OmniStreamEngine',
    'layer': 'Dart Interface',
    'components': [
      'OmniStreamController',
      'Stream extensions',
      'mergeStreams',
      'combineLatest',
    ],
    'operators': [
      'debounceTime', 'throttleTime', 'bufferCount', 'scan',
      'pairwise', 'retryStream', 'startWith', 'switchMap',
    ],
    'learned_logic': [
      'stream-single-broadcast-mode',
      'stream-controller-bridge',
      'debounce-timer-cancel-reset',
      'throttle-time-gate',
      'buffer-count-batch',
      'scan-accumulate-state',
      'switchMap-cancel-previous',
      'combineLatest-all-sources',
    ],
  };
}
