// ===========================================================================
// OMNI BLOC STATE ENGINE (SEMESTER 3 — BATCH 38.3)
// ===========================================================================
// Absorbed From  : flutter_bloc + provider + riverpod patterns
// Logic Inherited: Dart / UI Mobile Layer (BLoC Pattern State Management)
// ===========================================================================
//
// By studying flutter_bloc and the BLoC pattern, Mother learned that
// Dart's Stream-based architecture enables reactive UI state:
//   1. Events go IN, States come OUT (unidirectional)
//   2. Stream<State> drives UI rebuilds via StreamBuilder
//   3. Cubit = simplified BLoC without events (direct emit)
//   4. BlocObserver for cross-cutting concerns (logging, analytics)
//   5. Equatable states prevent unnecessary rebuilds

import 'dart:async';
import 'dart:collection';

// ---- Result Type (Monadic Error Handling) ----

sealed class BlocResult<T> {
  const BlocResult();
}

class BlocSuccess<T> extends BlocResult<T> {
  final T value;
  const BlocSuccess(this.value);
}

class BlocFailure<T> extends BlocResult<T> {
  final String error;
  const BlocFailure(this.error);
}

// ---- BLoC Observer (Cross-Cutting Concerns) ----

abstract class OmniBlocObserver {
  void onCreate(String blocName) {}
  void onEvent(String blocName, Object event) {}
  void onTransition(String blocName, Object currentState, Object nextState) {}
  void onChange(String blocName, Object currentState, Object nextState) {}
  void onError(String blocName, Object error) {}
  void onClose(String blocName) {}
}

/// Default observer that logs to console.
class LoggingBlocObserver extends OmniBlocObserver {
  final List<String> logs = [];

  @override
  void onCreate(String blocName) {
    logs.add('[CREATE] $blocName');
  }

  @override
  void onTransition(String blocName, Object currentState, Object nextState) {
    logs.add('[TRANSITION] $blocName: $currentState → $nextState');
  }

  @override
  void onError(String blocName, Object error) {
    logs.add('[ERROR] $blocName: $error');
  }

  @override
  void onClose(String blocName) {
    logs.add('[CLOSE] $blocName');
  }
}

// ---- Cubit (Simplified BLoC — Direct State Emission) ----

/// A Cubit emits state directly via `emit()` without events.
abstract class OmniCubit<State> {
  final String name;
  State _state;
  final StreamController<State> _controller = StreamController<State>.broadcast();
  final List<OmniBlocObserver> _observers = [];
  bool _isClosed = false;

  // Metrics
  int _totalEmissions = 0;
  int _totalSubscribers = 0;
  final List<State> _stateHistory = [];

  OmniCubit(this.name, State initialState) : _state = initialState {
    _stateHistory.add(initialState);
    for (final observer in _observers) {
      observer.onCreate(name);
    }
  }

  /// Current state.
  State get state => _state;

  /// State stream for StreamBuilder binding.
  Stream<State> get stream => _controller.stream;

  /// State history for debugging.
  List<State> get history => UnmodifiableListView(_stateHistory);

  /// Add an observer.
  void addObserver(OmniBlocObserver observer) {
    _observers.add(observer);
    observer.onCreate(name);
  }

  /// Emit a new state (drives UI rebuild).
  void emit(State newState) {
    if (_isClosed) return;
    if (newState == _state) return; // Skip if state hasn't changed

    final previous = _state;
    _state = newState;
    _stateHistory.add(newState);
    _totalEmissions++;

    for (final observer in _observers) {
      observer.onChange(name, previous as Object, newState as Object);
    }

    _controller.add(newState);
  }

  /// Subscribe to state changes.
  StreamSubscription<State> listen(void Function(State) onData) {
    _totalSubscribers++;
    return _controller.stream.listen(onData);
  }

  /// Close the cubit and release resources.
  Future<void> close() async {
    _isClosed = true;
    for (final observer in _observers) {
      observer.onClose(name);
    }
    await _controller.close();
  }

  bool get isClosed => _isClosed;

  Map<String, dynamic> get metrics => {
    'name': name,
    'total_emissions': _totalEmissions,
    'total_subscribers': _totalSubscribers,
    'history_size': _stateHistory.length,
    'is_closed': _isClosed,
  };
}

// ---- BLoC (Event-Driven State Management) ----

/// A BLoC processes events and emits states.
/// Events → BLoC → States (unidirectional data flow).
abstract class OmniBloc<Event, State> extends OmniCubit<State> {
  final StreamController<Event> _eventController =
      StreamController<Event>.broadcast();
  final Map<Type, Function> _handlers = {};
  int _totalEventsProcessed = 0;

  OmniBloc(String name, State initialState) : super(name, initialState) {
    _eventController.stream.listen(_onEvent);
  }

  /// Register an event handler for a specific event type.
  void on<E extends Event>(void Function(E event, void Function(State) emit) handler) {
    _handlers[E] = handler;
  }

  /// Add an event to the BLoC.
  void add(Event event) {
    if (isClosed) return;
    for (final observer in _observers) {
      observer.onEvent(name, event as Object);
    }
    _eventController.add(event);
  }

  void _onEvent(Event event) {
    _totalEventsProcessed++;
    final handler = _handlers[event.runtimeType];
    if (handler != null) {
      final previous = state;
      handler(event, (State newState) {
        for (final observer in _observers) {
          observer.onTransition(name, previous as Object, newState as Object);
        }
        emit(newState);
      });
    }
  }

  @override
  Future<void> close() async {
    await _eventController.close();
    await super.close();
  }

  @override
  Map<String, dynamic> get metrics => {
    ...super.metrics,
    'total_events_processed': _totalEventsProcessed,
    'registered_handlers': _handlers.keys.map((t) => t.toString()).toList(),
  };
}

// ---- Multi-BLoC Provider ----

/// Registry for multiple BLoCs, similar to MultiBlocProvider.
class OmniBlocProvider {
  final Map<Type, OmniCubit> _blocs = {};
  final List<OmniBlocObserver> _globalObservers = [];

  /// Register a BLoC/Cubit.
  void register<T extends OmniCubit>(T bloc) {
    _blocs[T] = bloc;
    for (final observer in _globalObservers) {
      bloc.addObserver(observer);
    }
  }

  /// Resolve a BLoC/Cubit by type.
  T? read<T extends OmniCubit>() {
    return _blocs[T] as T?;
  }

  /// Add a global observer to all registered BLoCs.
  void addGlobalObserver(OmniBlocObserver observer) {
    _globalObservers.add(observer);
    for (final bloc in _blocs.values) {
      bloc.addObserver(observer);
    }
  }

  /// Close all registered BLoCs.
  Future<void> dispose() async {
    for (final bloc in _blocs.values) {
      await bloc.close();
    }
    _blocs.clear();
  }

  int get blocCount => _blocs.length;

  // ---- Diagnostics ----

  Map<String, dynamic> diagnostics() => {
    'engine': 'OmniBlocStateEngine',
    'layer': 'Dart UI Mobile',
    'total_blocs': _blocs.length,
    'bloc_metrics': _blocs.map((type, bloc) =>
        MapEntry(type.toString(), bloc.metrics)),
    'global_observers': _globalObservers.length,
    'learned_logic': [
      'bloc-pattern-event-state',
      'cubit-simplified-direct-emit',
      'stream-controller-broadcast',
      'unidirectional-data-flow',
      'equatable-state-deduplication',
      'bloc-observer-cross-cutting',
      'multi-bloc-provider-registry',
      'stream-subscription-lifecycle',
    ],
  };
}
