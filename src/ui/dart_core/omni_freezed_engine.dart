// ===========================================================================
// OMNI FREEZED ENGINE (SEMESTER 3 — BATCH 38.8)
// ===========================================================================
// Absorbed From  : Freezed + json_serializable + built_value + equatable
// Logic Inherited: Dart / Interface Layer (Immutable Data Classes + Union Types)
// ===========================================================================
//
// By studying Freezed, Mother learned Dart immutable patterns:
//   1. Immutable data classes with == and hashCode by value
//   2. copyWith() for non-destructive updates
//   3. Union types via sealed classes with pattern matching
//   4. JSON serialization via toJson/fromJson factories
//   5. Deep immutability prevents accidental mutation

import 'dart:convert';

// ============================================================
// PART 1: Immutable Data Class Base
// ============================================================

/// Mixin for value equality.
mixin OmniEquatable {
  List<Object?> get props;

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    if (runtimeType != other.runtimeType) return false;
    if (other is! OmniEquatable) return false;
    final otherProps = other.props;
    if (props.length != otherProps.length) return false;
    for (var i = 0; i < props.length; i++) {
      if (props[i] != otherProps[i]) return false;
    }
    return true;
  }

  @override
  int get hashCode {
    return Object.hashAll(props);
  }
}

// ============================================================
// PART 2: Generic Immutable Model
// ============================================================

/// Base for immutable models with copyWith and serde.
abstract class OmniModel with OmniEquatable {
  const OmniModel();

  /// Serialize to JSON map.
  Map<String, dynamic> toJson();

  /// Pretty-print JSON.
  String toJsonString() => const JsonEncoder.withIndent('  ').convert(toJson());

  @override
  String toString() {
    final className = runtimeType.toString();
    final fields = toJson().entries.map((e) => '${e.key}: ${e.value}').join(', ');
    return '$className($fields)';
  }
}

// ============================================================
// PART 3: Example Models (Freezed-style)
// ============================================================

/// User model with copyWith.
class User extends OmniModel {
  final String id;
  final String name;
  final String email;
  final int age;
  final DateTime createdAt;
  final bool isActive;

  const User({
    required this.id,
    required this.name,
    required this.email,
    required this.age,
    required this.createdAt,
    this.isActive = true,
  });

  /// Non-destructive update.
  User copyWith({
    String? id,
    String? name,
    String? email,
    int? age,
    DateTime? createdAt,
    bool? isActive,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      age: age ?? this.age,
      createdAt: createdAt ?? this.createdAt,
      isActive: isActive ?? this.isActive,
    );
  }

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      name: json['name'] as String,
      email: json['email'] as String,
      age: json['age'] as int,
      createdAt: DateTime.parse(json['createdAt'] as String),
      isActive: json['isActive'] as bool? ?? true,
    );
  }

  @override
  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'email': email,
    'age': age,
    'createdAt': createdAt.toIso8601String(),
    'isActive': isActive,
  };

  @override
  List<Object?> get props => [id, name, email, age, createdAt, isActive];
}

// ============================================================
// PART 4: Union Types (Sealed pattern)
// ============================================================

/// Network result as a sealed union type.
sealed class NetworkResult<T> {
  const NetworkResult();

  /// Pattern match on all cases.
  R when<R>({
    required R Function(T data) success,
    required R Function(String message, int? statusCode) error,
    required R Function() loading,
  }) {
    final self = this;
    if (self is NetworkSuccess<T>) return success(self.data);
    if (self is NetworkError<T>) return error(self.message, self.statusCode);
    if (self is NetworkLoading<T>) return loading();
    throw StateError('Unknown state');
  }

  /// Pattern match with optional handlers.
  R maybeWhen<R>({
    R Function(T data)? success,
    R Function(String message, int? statusCode)? error,
    R Function()? loading,
    required R Function() orElse,
  }) {
    final self = this;
    if (self is NetworkSuccess<T> && success != null) return success(self.data);
    if (self is NetworkError<T> && error != null) return error(self.message, self.statusCode);
    if (self is NetworkLoading<T> && loading != null) return loading();
    return orElse();
  }

  /// Map the success value.
  NetworkResult<R> map<R>(R Function(T) transform) {
    return when(
      success: (data) => NetworkResult.success(transform(data)),
      error: (msg, code) => NetworkResult.error(msg, statusCode: code),
      loading: () => NetworkResult.loading(),
    );
  }

  /// Factory constructors.
  factory NetworkResult.success(T data) = NetworkSuccess<T>;
  factory NetworkResult.error(String message, {int? statusCode}) = NetworkError<T>;
  factory NetworkResult.loading() = NetworkLoading<T>;
}

class NetworkSuccess<T> extends NetworkResult<T> {
  final T data;
  const NetworkSuccess(this.data);

  @override
  String toString() => 'NetworkSuccess($data)';
}

class NetworkError<T> extends NetworkResult<T> {
  final String message;
  final int? statusCode;
  const NetworkError(this.message, {this.statusCode});

  @override
  String toString() => 'NetworkError($message, status: $statusCode)';
}

class NetworkLoading<T> extends NetworkResult<T> {
  const NetworkLoading();

  @override
  String toString() => 'NetworkLoading()';
}

// ============================================================
// PART 5: Pagination State (Union Type)
// ============================================================

sealed class PaginationState<T> {
  const PaginationState();

  R when<R>({
    required R Function() initial,
    required R Function() loading,
    required R Function(List<T> items, bool hasMore, int page) loaded,
    required R Function(String message) error,
  }) {
    final self = this;
    if (self is PaginationInitial<T>) return initial();
    if (self is PaginationLoading<T>) return loading();
    if (self is PaginationLoaded<T>) return loaded(self.items, self.hasMore, self.page);
    if (self is PaginationError<T>) return error(self.message);
    throw StateError('Unknown state');
  }
}

class PaginationInitial<T> extends PaginationState<T> { const PaginationInitial(); }
class PaginationLoading<T> extends PaginationState<T> { const PaginationLoading(); }
class PaginationLoaded<T> extends PaginationState<T> {
  final List<T> items;
  final bool hasMore;
  final int page;
  const PaginationLoaded(this.items, {required this.hasMore, required this.page});
}
class PaginationError<T> extends PaginationState<T> {
  final String message;
  const PaginationError(this.message);
}

// ============================================================
// Diagnostics
// ============================================================

Map<String, dynamic> freezedDiagnostics() {
  return {
    'engine': 'OmniFreezedEngine',
    'layer': 'Dart Interface',
    'components': [
      'OmniModel', 'OmniEquatable', 'User (immutable)',
      'NetworkResult (sealed union)', 'PaginationState (sealed union)',
    ],
    'features': [
      'copyWith', 'toJson/fromJson', 'value equality',
      'when/maybeWhen pattern matching', 'sealed class unions',
    ],
    'learned_logic': [
      'freezed-immutable-data-class',
      'copyWith-non-destructive-update',
      'value-equality-props-list',
      'sealed-union-type-exhaustive',
      'when-pattern-match-all-cases',
      'maybeWhen-optional-handlers',
      'json-serialization-factories',
      'deep-immutability-const',
    ],
  };
}
