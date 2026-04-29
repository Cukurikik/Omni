using System;

namespace Omni.Business.MLFlowTracker
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public enum ExperimentState
    {
        Running,
        Scheduled,
        Finished,
        Failed,
        Killed
    }

    public class StateMachinePolicy
    {
        public OmniResult<bool> ValidateTransition(ExperimentState current_state, ExperimentState target_state)
        {
            // Business logic for MLFlow experiment state transitions
            if (current_state == ExperimentState.Finished || current_state == ExperimentState.Failed || current_state == ExperimentState.Killed)
            {
                return new OmniResult<bool>(new InvalidOperationException($"Cannot transition from terminal state {current_state}"));
            }

            if (current_state == ExperimentState.Scheduled && target_state != ExperimentState.Running && target_state != ExperimentState.Killed)
            {
                return new OmniResult<bool>(new InvalidOperationException($"Invalid transition from Scheduled to {target_state}"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
