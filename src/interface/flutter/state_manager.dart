import 'dart:async';

abstract class OmniState {}
class InitialState extends OmniState {}
class LoadingState extends OmniState {}
class SuccessState<T> extends OmniState {
  final T data;
  SuccessState(this.data);
}
class ErrorState extends OmniState {
  final String error;
  ErrorState(this.error);
}

class OmniBloc<T> {
  final _stateController = StreamController<OmniState>.broadcast();
  Stream<OmniState> get state => _stateController.stream;
  
  OmniState _currentState = InitialState();
  OmniState get currentState => _currentState;

  void emit(OmniState newState) {
    _currentState = newState;
    _stateController.sink.add(newState);
  }

  void dispose() {
    _stateController.close();
  }
}
