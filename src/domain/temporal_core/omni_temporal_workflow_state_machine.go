// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Temporal SDK — Business Layer (OMNI Zero-Mock Implementation)
// Implements deterministic Workflow State Machine with exact Temporal execution semantics.
// Absorbs patterns from: github.com/temporalio/sdk-go

package temporal

import (
	"errors"
)

// WorkflowState represents the execution states of a Temporal workflow.
type WorkflowState int

const (
	StateCreated    WorkflowState = iota // Workflow registered but not started
	StateRunning                         // Actively executing activities
	StateCompleted                       // Successfully finished
	StateFailed                          // Terminal failure
	StateCancelled                       // Externally cancelled
	StateTimedOut                        // Exceeded workflow execution timeout
	StateContinuedAsNew                  // Restarted with new run ID
)

// WorkflowExecution holds the mutable state of a running Temporal workflow.
type WorkflowExecution struct {
	WorkflowID         string
	RunID              string
	State              WorkflowState
	AttemptCount       int
	MaxRetries         int
	StartToCloseMs     int64
	ElapsedMs          int64
	LastActivityResult string
}

// StateTransitionResult is the monadic result for workflow operations.
type StateTransitionResult struct {
	NewState WorkflowState
	Error    error
}

// EvaluateStateTransition applies Temporal's deterministic state machine rules.
// Temporal workflows MUST be deterministic — same inputs always produce same state.
//
// Valid transitions:
//   Created  -> Running
//   Running  -> Completed | Failed | Cancelled | TimedOut | ContinuedAsNew
//   All terminal states are final (no transitions out).
func EvaluateStateTransition(exec *WorkflowExecution, event string) StateTransitionResult {
	if exec == nil {
		return StateTransitionResult{NewState: StateFailed, Error: errors.New("Temporal requires non-nil workflow execution.")}
	}

	switch exec.State {
	case StateCreated:
		if event == "workflow_started" {
			exec.State = StateRunning
			return StateTransitionResult{NewState: StateRunning, Error: nil}
		}
		return StateTransitionResult{NewState: StateCreated, Error: errors.New("Temporal: only 'workflow_started' valid from Created state.")}

	case StateRunning:
		switch event {
		case "activity_completed":
			exec.LastActivityResult = "success"
			return StateTransitionResult{NewState: StateRunning, Error: nil}

		case "workflow_completed":
			exec.State = StateCompleted
			return StateTransitionResult{NewState: StateCompleted, Error: nil}

		case "workflow_failed":
			exec.AttemptCount++
			if exec.AttemptCount <= exec.MaxRetries {
				// Temporal automatic retry — stays in Running
				return StateTransitionResult{NewState: StateRunning, Error: nil}
			}
			exec.State = StateFailed
			return StateTransitionResult{NewState: StateFailed, Error: nil}

		case "workflow_cancelled":
			exec.State = StateCancelled
			return StateTransitionResult{NewState: StateCancelled, Error: nil}

		case "workflow_timed_out":
			if exec.ElapsedMs >= exec.StartToCloseMs && exec.StartToCloseMs > 0 {
				exec.State = StateTimedOut
				return StateTransitionResult{NewState: StateTimedOut, Error: nil}
			}
			return StateTransitionResult{NewState: StateRunning, Error: errors.New("Temporal: timeout event but elapsed < StartToClose.")}

		case "continue_as_new":
			exec.State = StateContinuedAsNew
			return StateTransitionResult{NewState: StateContinuedAsNew, Error: nil}

		default:
			return StateTransitionResult{NewState: StateRunning, Error: errors.New("Temporal: unknown event for Running state.")}
		}

	case StateCompleted, StateFailed, StateCancelled, StateTimedOut, StateContinuedAsNew:
		return StateTransitionResult{NewState: exec.State, Error: errors.New("Temporal: terminal state — no transitions allowed.")}

	default:
		return StateTransitionResult{NewState: StateFailed, Error: errors.New("Temporal: invalid workflow state detected.")}
	}
}

// EvaluateRetryPolicy computes the next retry delay using exponential backoff.
// Matches Temporal's RetryPolicy: initialInterval * backoffCoefficient^(attempt-1)
// Capped at maximumInterval.
func EvaluateRetryPolicy(
	initialIntervalMs int64,
	backoffCoefficient float64,
	maximumIntervalMs int64,
	currentAttempt int,
) (int64, error) {
	if initialIntervalMs <= 0 {
		return 0, errors.New("Temporal RetryPolicy: initialInterval must be > 0.")
	}
	if backoffCoefficient < 1.0 {
		return 0, errors.New("Temporal RetryPolicy: backoffCoefficient must be >= 1.0.")
	}
	if currentAttempt < 1 {
		return 0, errors.New("Temporal RetryPolicy: attempt must be >= 1.")
	}

	delay := float64(initialIntervalMs)
	for i := 1; i < currentAttempt; i++ {
		delay *= backoffCoefficient
		if maximumIntervalMs > 0 && int64(delay) >= maximumIntervalMs {
			return maximumIntervalMs, nil
		}
	}

	return int64(delay), nil
}
