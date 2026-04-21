// ===========================================================================
// OMNI RESULT PIPELINE ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : FluentResults + OneOf + ErrorOr + LanguageExt
// Logic Inherited: C# / Domain Layer (Railway-Oriented Result Pipeline)
// ===========================================================================
//
// By studying FluentResults and ErrorOr, Mother learned C# result patterns:
//   1. Result<T> eliminates exception-driven control flow
//   2. Bind/Map/Match enable monadic chaining
//   3. ErrorOr collects multiple validation errors
//   4. Pipeline behaviors wrap each step with cross-cutting concerns
//   5. C# record types make error hierarchies concise

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Omni.Domain.ResultPipeline
{
    // ============================================================
    // PART 1: Error Hierarchy
    // ============================================================

    /// <summary>Base error type with code, message, and metadata.</summary>
    public record OmniError(
        string Code,
        string Message,
        ErrorType Type = ErrorType.Failure,
        Dictionary<string, object>? Metadata = null
    );

    public enum ErrorType
    {
        Failure,
        Validation,
        NotFound,
        Conflict,
        Unauthorized,
        Forbidden,
        Unexpected
    }

    // ============================================================
    // PART 2: Result<T> Monad
    // ============================================================

    /// <summary>
    /// Monadic Result type: either Success(T) or Failure(errors).
    /// No exceptions for control flow.
    /// </summary>
    public readonly struct Result<T>
    {
        private readonly T? _value;
        private readonly List<OmniError>? _errors;
        private readonly bool _isSuccess;

        private Result(T value)
        {
            _value = value;
            _errors = null;
            _isSuccess = true;
        }

        private Result(List<OmniError> errors)
        {
            _value = default;
            _errors = errors;
            _isSuccess = false;
        }

        public bool IsSuccess => _isSuccess;
        public bool IsFailure => !_isSuccess;

        public T Value => _isSuccess
            ? _value!
            : throw new InvalidOperationException("Cannot access Value on a failed Result");

        public IReadOnlyList<OmniError> Errors => _errors?.AsReadOnly()
            ?? (IReadOnlyList<OmniError>)Array.Empty<OmniError>();

        public OmniError FirstError => Errors.First();

        // Factory methods
        public static Result<T> Success(T value) => new(value);
        public static Result<T> Fail(string code, string message) =>
            new(new List<OmniError> { new(code, message) });
        public static Result<T> Fail(OmniError error) =>
            new(new List<OmniError> { error });
        public static Result<T> Fail(IEnumerable<OmniError> errors) =>
            new(new List<OmniError>(errors));

        // Implicit conversions
        public static implicit operator Result<T>(T value) => Success(value);
        public static implicit operator Result<T>(OmniError error) => Fail(error);

        // ============================================================
        // Monadic Operations
        // ============================================================

        /// <summary>Map: transform value if success.</summary>
        public Result<U> Map<U>(Func<T, U> mapper)
        {
            if (IsFailure) return Result<U>.Fail(_errors!);
            return Result<U>.Success(mapper(_value!));
        }

        /// <summary>Bind: chain with another Result-producing function.</summary>
        public Result<U> Bind<U>(Func<T, Result<U>> binder)
        {
            if (IsFailure) return Result<U>.Fail(_errors!);
            return binder(_value!);
        }

        /// <summary>Async bind.</summary>
        public async Task<Result<U>> BindAsync<U>(Func<T, Task<Result<U>>> binder)
        {
            if (IsFailure) return Result<U>.Fail(_errors!);
            return await binder(_value!);
        }

        /// <summary>Match: handle both cases.</summary>
        public U Match<U>(Func<T, U> onSuccess, Func<IReadOnlyList<OmniError>, U> onFailure)
        {
            return _isSuccess ? onSuccess(_value!) : onFailure(Errors);
        }

        /// <summary>Tap: execute side effect without changing result.</summary>
        public Result<T> Tap(Action<T> action)
        {
            if (IsSuccess) action(_value!);
            return this;
        }

        /// <summary>TapError: execute side effect on failure.</summary>
        public Result<T> TapError(Action<IReadOnlyList<OmniError>> action)
        {
            if (IsFailure) action(Errors);
            return this;
        }

        /// <summary>Ensure: add validation check.</summary>
        public Result<T> Ensure(Func<T, bool> predicate, OmniError error)
        {
            if (IsFailure) return this;
            if (!predicate(_value!))
            {
                var errors = new List<OmniError>(_errors ?? new List<OmniError>()) { error };
                return Result<T>.Fail(errors);
            }
            return this;
        }

        /// <summary>Or: provide fallback on failure.</summary>
        public Result<T> Or(Func<Result<T>> fallback)
        {
            return IsSuccess ? this : fallback();
        }

        /// <summary>GetValueOrDefault: extract value or use default.</summary>
        public T GetValueOrDefault(T defaultValue = default!)
        {
            return IsSuccess ? _value! : defaultValue;
        }

        public override string ToString()
        {
            return IsSuccess
                ? $"Success({_value})"
                : $"Failure({string.Join(", ", Errors.Select(e => e.Message))})";
        }
    }

    // ============================================================
    // PART 3: Result Pipeline (Railway-Oriented)
    // ============================================================

    /// <summary>
    /// Fluent pipeline that chains Result-producing steps.
    /// Short-circuits on first failure.
    /// </summary>
    public class Pipeline<T>
    {
        private readonly List<(string Name, Func<T, Result<T>> Step)> _steps = new();
        private readonly List<Func<string, T, T>> _beforeHooks = new();
        private readonly List<Func<string, Result<T>, Result<T>>> _afterHooks = new();
        private int _totalExecutions = 0;

        public Pipeline<T> AddStep(string name, Func<T, Result<T>> step)
        {
            _steps.Add((name, step));
            return this;
        }

        public Pipeline<T> Before(Func<string, T, T> hook)
        {
            _beforeHooks.Add(hook);
            return this;
        }

        public Pipeline<T> After(Func<string, Result<T>, Result<T>> hook)
        {
            _afterHooks.Add(hook);
            return this;
        }

        public Result<T> Execute(T input)
        {
            _totalExecutions++;
            Result<T> current = Result<T>.Success(input);

            foreach (var (name, step) in _steps)
            {
                if (current.IsFailure) break;

                // Before hooks
                var value = current.Value;
                foreach (var hook in _beforeHooks)
                {
                    value = hook(name, value);
                }

                // Execute step
                current = step(value);

                // After hooks
                foreach (var hook in _afterHooks)
                {
                    current = hook(name, current);
                }
            }

            return current;
        }

        public int TotalExecutions => _totalExecutions;
        public int StepCount => _steps.Count;
    }

    // ============================================================
    // PART 4: Validation Result (Accumulating Errors)
    // ============================================================

    /// <summary>
    /// Accumulates ALL validation errors instead of short-circuiting.
    /// </summary>
    public class ValidationResult<T>
    {
        private readonly T? _value;
        private readonly List<OmniError> _errors = new();

        public ValidationResult(T value)
        {
            _value = value;
        }

        public bool IsValid => _errors.Count == 0;
        public T Value => IsValid ? _value! : throw new InvalidOperationException("Validation failed");
        public IReadOnlyList<OmniError> Errors => _errors.AsReadOnly();

        public ValidationResult<T> Validate(
            Func<T, bool> predicate,
            string code,
            string message)
        {
            if (!predicate(_value!))
            {
                _errors.Add(new OmniError(code, message, ErrorType.Validation));
            }
            return this;
        }

        public Result<T> ToResult()
        {
            return IsValid
                ? Result<T>.Success(_value!)
                : Result<T>.Fail(_errors);
        }
    }

    // ============================================================
    // Diagnostics
    // ============================================================

    public static class ResultPipelineDiagnostics
    {
        public static Dictionary<string, object> GetDiagnostics()
        {
            return new Dictionary<string, object>
            {
                ["engine"] = "OmniResultPipelineEngine",
                ["layer"] = "C# Domain",
                ["components"] = new[]
                {
                    "Result<T>", "OmniError", "Pipeline<T>", "ValidationResult<T>"
                },
                ["monadic_ops"] = new[]
                {
                    "Map", "Bind", "BindAsync", "Match", "Tap", "TapError", "Ensure", "Or"
                },
                ["learned_logic"] = new[]
                {
                    "result-monad-no-exceptions",
                    "bind-chain-short-circuit",
                    "map-transform-success-only",
                    "match-exhaustive-both-cases",
                    "ensure-inline-validation",
                    "validation-accumulate-errors",
                    "pipeline-before-after-hooks",
                    "implicit-conversion-ergonomic"
                }
            };
        }
    }
}
