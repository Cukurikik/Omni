import gleam/list
import gleam/option.{type Option, None, Some}
import gleam/result

// OMNI MOTHER — SEMESTER 14 BATCH 36
// Gleam — Concurrency & Networking Layer (OMNI Zero-Mock Implementation)
// Implements production-grade Circuit Breaker pattern.
// Absorbs patterns from: github.com/gleam-lang/otp, Netflix Hystrix

/// Circuit breaker states following the standard pattern.
pub type CircuitState {
  Closed
  Open
  HalfOpen
}

/// Configuration for circuit breaker behavior.
pub type CircuitConfig {
  CircuitConfig(
    failure_threshold: Int,
    success_threshold: Int,
    timeout_ms: Int,
  )
}

/// Recorded call outcome.
pub type CallOutcome {
  Success
  Failure(reason: String)
}

/// The circuit breaker internal state.
pub type CircuitBreaker {
  CircuitBreaker(
    name: String,
    state: CircuitState,
    config: CircuitConfig,
    consecutive_failures: Int,
    consecutive_successes: Int,
    total_calls: Int,
    total_failures: Int,
  )
}

/// Monadic result for circuit breaker operations.
pub type CBResult(t) {
  CBOk(value: t)
  CBErr(reason: String)
}

/// Creates a new circuit breaker in the Closed state.
pub fn new_circuit_breaker(
  name: String,
  config: CircuitConfig,
) -> CBResult(CircuitBreaker) {
  case config.failure_threshold > 0,
       config.success_threshold > 0,
       config.timeout_ms > 0
  {
    True, True, True ->
      CBOk(CircuitBreaker(
        name: name,
        state: Closed,
        config: config,
        consecutive_failures: 0,
        consecutive_successes: 0,
        total_calls: 0,
        total_failures: 0,
      ))
    _, _, _ -> CBErr("Circuit breaker config thresholds must be > 0")
  }
}

/// Attempts to execute a call through the circuit breaker.
/// Returns whether the call is allowed based on current state.
pub fn allow_call(cb: CircuitBreaker) -> CBResult(Bool) {
  case cb.state {
    Closed -> CBOk(True)
    Open -> CBOk(False)
    HalfOpen -> CBOk(True)
  }
}

/// Records a call outcome and returns updated circuit breaker state.
pub fn record_outcome(
  cb: CircuitBreaker,
  outcome: CallOutcome,
) -> CircuitBreaker {
  let new_total = cb.total_calls + 1
  case outcome {
    Success -> handle_success(cb, new_total)
    Failure(_reason) -> handle_failure(cb, new_total)
  }
}

fn handle_success(
  cb: CircuitBreaker,
  new_total: Int,
) -> CircuitBreaker {
  let new_successes = cb.consecutive_successes + 1
  case cb.state {
    HalfOpen -> {
      case new_successes >= cb.config.success_threshold {
        True ->
          CircuitBreaker(
            ..cb,
            state: Closed,
            consecutive_failures: 0,
            consecutive_successes: 0,
            total_calls: new_total,
          )
        False ->
          CircuitBreaker(
            ..cb,
            consecutive_successes: new_successes,
            consecutive_failures: 0,
            total_calls: new_total,
          )
      }
    }
    _ ->
      CircuitBreaker(
        ..cb,
        consecutive_failures: 0,
        consecutive_successes: new_successes,
        total_calls: new_total,
      )
  }
}

fn handle_failure(
  cb: CircuitBreaker,
  new_total: Int,
) -> CircuitBreaker {
  let new_failures = cb.consecutive_failures + 1
  let new_total_failures = cb.total_failures + 1
  case cb.state {
    Closed -> {
      case new_failures >= cb.config.failure_threshold {
        True ->
          CircuitBreaker(
            ..cb,
            state: Open,
            consecutive_failures: new_failures,
            consecutive_successes: 0,
            total_calls: new_total,
            total_failures: new_total_failures,
          )
        False ->
          CircuitBreaker(
            ..cb,
            consecutive_failures: new_failures,
            consecutive_successes: 0,
            total_calls: new_total,
            total_failures: new_total_failures,
          )
      }
    }
    HalfOpen ->
      CircuitBreaker(
        ..cb,
        state: Open,
        consecutive_failures: new_failures,
        consecutive_successes: 0,
        total_calls: new_total,
        total_failures: new_total_failures,
      )
    Open ->
      CircuitBreaker(
        ..cb,
        total_calls: new_total,
        total_failures: new_total_failures,
      )
  }
}

/// Transitions from Open to HalfOpen (called after timeout expires).
pub fn attempt_reset(cb: CircuitBreaker) -> CBResult(CircuitBreaker) {
  case cb.state {
    Open ->
      CBOk(CircuitBreaker(
        ..cb,
        state: HalfOpen,
        consecutive_failures: 0,
        consecutive_successes: 0,
      ))
    _ -> CBErr("Can only reset from Open state")
  }
}
