import 'package:flutter_bloc/flutter_bloc.dart';

abstract class DashboardEvent {}
class LoadMetrics extends DashboardEvent {}

class DashboardState {
  final int requests;
  final double latency;
  DashboardState({this.requests = 0, this.latency = 0.0});
}

class DashboardBloc extends Bloc<DashboardEvent, DashboardState> {
  DashboardBloc() : super(DashboardState()) {
    on<LoadMetrics>((event, emit) {
      // Simulate fetching metrics
      emit(DashboardState(requests: state.requests + 1, latency: 12.5));
    });
  }
}
