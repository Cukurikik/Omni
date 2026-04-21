// ===========================================================================
// OMNI SAGA ORCHESTRATOR ENGINE (SEMESTER 3 — BATCH 38.2)
// ===========================================================================
// Absorbed From  : MassTransit Saga + NServiceBus + Eventual consistency
// Logic Inherited: C# / Domain Layer (Distributed Transaction Saga Pattern)
// ===========================================================================
//
// By studying MassTransit's Automatonymous and NServiceBus sagas, Mother
// learned that distributed transactions require compensating actions:
//   1. Each step has an Execute and a Compensate action
//   2. If any step fails, all previous steps are compensated in reverse
//   3. State machine tracks saga progress persistently
//   4. Idempotency keys prevent duplicate processing
//   5. Timeout-based recovery for hanging steps

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Omni.Domain.Saga
{
    /// <summary>
    /// Represents the outcome of a saga step — monadic Result type.
    /// </summary>
    public sealed class SagaResult<T>
    {
        public T Value { get; }
        public string Error { get; }
        public bool IsSuccess { get; }

        private SagaResult(T value, string error, bool success)
        {
            Value = value;
            Error = error;
            IsSuccess = success;
        }

        public static SagaResult<T> Ok(T value) => new(value, null, true);
        public static SagaResult<T> Fail(string error) => new(default, error, false);

        public SagaResult<U> Map<U>(Func<T, U> fn) =>
            IsSuccess ? SagaResult<U>.Ok(fn(Value)) : SagaResult<U>.Fail(Error);

        public SagaResult<U> FlatMap<U>(Func<T, SagaResult<U>> fn) =>
            IsSuccess ? fn(Value) : SagaResult<U>.Fail(Error);
    }

    /// <summary>
    /// A single step in a saga with execute and compensate actions.
    /// </summary>
    public sealed class SagaStep
    {
        public string Name { get; }
        public Func<Dictionary<string, object>, SagaResult<object>> Execute { get; }
        public Func<Dictionary<string, object>, SagaResult<object>> Compensate { get; }
        public TimeSpan Timeout { get; }
        public int MaxRetries { get; }

        public SagaStep(
            string name,
            Func<Dictionary<string, object>, SagaResult<object>> execute,
            Func<Dictionary<string, object>, SagaResult<object>> compensate,
            TimeSpan? timeout = null,
            int maxRetries = 0)
        {
            Name = name ?? throw new ArgumentNullException(nameof(name));
            Execute = execute ?? throw new ArgumentNullException(nameof(execute));
            Compensate = compensate ?? throw new ArgumentNullException(nameof(compensate));
            Timeout = timeout ?? TimeSpan.FromSeconds(30);
            MaxRetries = maxRetries;
        }
    }

    /// <summary>
    /// Tracks the execution state of a saga instance.
    /// </summary>
    public enum SagaState
    {
        NotStarted,
        InProgress,
        Completed,
        Compensating,
        Compensated,
        Failed
    }

    /// <summary>
    /// Record of an executed step (for compensation tracking).
    /// </summary>
    public sealed class StepRecord
    {
        public string StepName { get; set; }
        public bool Succeeded { get; set; }
        public DateTime ExecutedAt { get; set; }
        public TimeSpan Duration { get; set; }
        public string Error { get; set; }
        public int AttemptNumber { get; set; }
    }

    /// <summary>
    /// Saga instance — tracks state, execution history, and context.
    /// </summary>
    public sealed class SagaInstance
    {
        public string SagaId { get; }
        public string IdempotencyKey { get; }
        public SagaState State { get; set; }
        public Dictionary<string, object> Context { get; }
        public List<StepRecord> ExecutionLog { get; }
        public List<StepRecord> CompensationLog { get; }
        public DateTime CreatedAt { get; }
        public DateTime? CompletedAt { get; set; }

        public SagaInstance(string idempotencyKey)
        {
            SagaId = Guid.NewGuid().ToString("N")[..8];
            IdempotencyKey = idempotencyKey;
            State = SagaState.NotStarted;
            Context = new Dictionary<string, object>();
            ExecutionLog = new List<StepRecord>();
            CompensationLog = new List<StepRecord>();
            CreatedAt = DateTime.UtcNow;
        }
    }

    /// <summary>
    /// OMNI Saga Orchestrator — executes multi-step distributed transactions
    /// with automatic compensation on failure.
    /// </summary>
    public sealed class OmniSagaOrchestratorEngine
    {
        private readonly List<SagaStep> _steps;
        private readonly Dictionary<string, SagaInstance> _sagas;
        private readonly HashSet<string> _processedKeys; // Idempotency guard
        private long _totalSagasStarted;
        private long _totalSagasCompleted;
        private long _totalSagasCompensated;
        private long _totalSagasFailed;
        private long _totalStepsExecuted;
        private long _totalCompensations;

        public OmniSagaOrchestratorEngine()
        {
            _steps = new List<SagaStep>();
            _sagas = new Dictionary<string, SagaInstance>();
            _processedKeys = new HashSet<string>();
        }

        /// <summary>Add a step to the saga definition.</summary>
        public OmniSagaOrchestratorEngine AddStep(SagaStep step)
        {
            _steps.Add(step);
            return this;
        }

        /// <summary>
        /// Execute the saga. If any step fails, compensate all previously
        /// completed steps in reverse order.
        /// </summary>
        public SagaResult<SagaInstance> Execute(string idempotencyKey,
            Dictionary<string, object> initialContext = null)
        {
            // Idempotency check
            if (_processedKeys.Contains(idempotencyKey))
                return SagaResult<SagaInstance>.Fail(
                    $"Saga already processed: {idempotencyKey}");

            var saga = new SagaInstance(idempotencyKey);
            if (initialContext != null)
            {
                foreach (var kv in initialContext)
                    saga.Context[kv.Key] = kv.Value;
            }

            _sagas[saga.SagaId] = saga;
            _processedKeys.Add(idempotencyKey);
            _totalSagasStarted++;

            saga.State = SagaState.InProgress;
            var completedSteps = new Stack<int>(); // Track for compensation

            for (int i = 0; i < _steps.Count; i++)
            {
                var step = _steps[i];
                var record = new StepRecord
                {
                    StepName = step.Name,
                    AttemptNumber = 1
                };

                var start = DateTime.UtcNow;
                SagaResult<object> result = null;

                // Retry loop
                for (int attempt = 0; attempt <= step.MaxRetries; attempt++)
                {
                    record.AttemptNumber = attempt + 1;
                    result = step.Execute(saga.Context);
                    _totalStepsExecuted++;

                    if (result.IsSuccess) break;
                }

                record.Duration = DateTime.UtcNow - start;
                record.ExecutedAt = start;

                if (result.IsSuccess)
                {
                    record.Succeeded = true;
                    saga.ExecutionLog.Add(record);
                    completedSteps.Push(i);
                }
                else
                {
                    record.Succeeded = false;
                    record.Error = result.Error;
                    saga.ExecutionLog.Add(record);

                    // COMPENSATE in reverse order
                    saga.State = SagaState.Compensating;
                    Compensate(saga, completedSteps);
                    return SagaResult<SagaInstance>.Fail(
                        $"Step '{step.Name}' failed: {result.Error}. " +
                        $"Compensated {completedSteps.Count} steps.");
                }
            }

            saga.State = SagaState.Completed;
            saga.CompletedAt = DateTime.UtcNow;
            _totalSagasCompleted++;
            return SagaResult<SagaInstance>.Ok(saga);
        }

        private void Compensate(SagaInstance saga, Stack<int> completedSteps)
        {
            while (completedSteps.Count > 0)
            {
                int stepIdx = completedSteps.Pop();
                var step = _steps[stepIdx];
                var start = DateTime.UtcNow;

                var compResult = step.Compensate(saga.Context);
                _totalCompensations++;

                saga.CompensationLog.Add(new StepRecord
                {
                    StepName = step.Name + " [COMPENSATE]",
                    Succeeded = compResult.IsSuccess,
                    ExecutedAt = start,
                    Duration = DateTime.UtcNow - start,
                    Error = compResult.IsSuccess ? null : compResult.Error
                });
            }

            saga.State = SagaState.Compensated;
            _totalSagasCompensated++;
        }

        /// <summary>Get a saga instance by ID.</summary>
        public SagaInstance GetSaga(string sagaId) =>
            _sagas.TryGetValue(sagaId, out var saga) ? saga : null;

        /// <summary>OMNI Engine Registry diagnostics.</summary>
        public Dictionary<string, object> Diagnostics()
        {
            return new Dictionary<string, object>
            {
                ["engine"] = "OmniSagaOrchestratorEngine",
                ["layer"] = "C# Domain",
                ["step_count"] = _steps.Count,
                ["total_sagas_started"] = _totalSagasStarted,
                ["total_sagas_completed"] = _totalSagasCompleted,
                ["total_sagas_compensated"] = _totalSagasCompensated,
                ["total_steps_executed"] = _totalStepsExecuted,
                ["total_compensations"] = _totalCompensations,
                ["active_sagas"] = _sagas.Count,
                ["learned_logic"] = new[]
                {
                    "saga-pattern-compensating-actions",
                    "reverse-order-compensation",
                    "idempotency-key-deduplication",
                    "step-retry-with-max-attempts",
                    "state-machine-saga-lifecycle",
                    "stack-based-compensation-tracking",
                    "monadic-result-error-handling",
                    "context-propagation-dictionary"
                }
            };
        }
    }
}
