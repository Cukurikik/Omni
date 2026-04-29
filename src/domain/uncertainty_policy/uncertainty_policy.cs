using System;

namespace Omni.Domain.UncertaintyPolicy
{
    // OMNI Engine: Uncertainty-o Domain Policy
    // C# Aggregate Policy for generation confidence mathematical bounds.

    public class PolicyError : Exception
    {
        public PolicyError(string message) : base(message) { }
    }

    public class Result<T>
    {
        public T Value { get; }
        public PolicyError Error { get; }
        public bool IsOk => Error == null;

        private Result(T value, PolicyError error)
        {
            Value = value;
            Error = error;
        }

        public static Result<T> Ok(T value) => new Result<T>(value, null);
        public static Result<T> Err(string errorMsg) => new Result<T>(default(T), new PolicyError(errorMsg));

        public T Unwrap()
        {
            if (!IsOk) throw Error;
            return Value;
        }
    }

    public class UncertaintyAggregate
    {
        private readonly double _confidenceHardBoundary;

        public UncertaintyAggregate(double safeBoundary = 0.55)
        {
            _confidenceHardBoundary = safeBoundary;
        }

        public Result<bool> ValidateOutputConfidence(double confidenceScore, bool isHighStakes)
        {
            if (confidenceScore < 0.0 || confidenceScore > 1.0)
            {
                return Result<bool>.Err("Confidence mathematical limit breached. Must be [0.0, 1.0]");
            }

            double requiredThreshold = isHighStakes ? 0.90 : _confidenceHardBoundary;

            if (confidenceScore < requiredThreshold)
            {
                return Result<bool>.Err($"Confidence {confidenceScore} rejected. Belows policy threshold {requiredThreshold}");
            }

            return Result<bool>.Ok(true);
        }

        public Result<double> AssessEpistemicFallout(double epistemicVariance)
        {
            if (epistemicVariance < 0.0)
            {
                 return Result<double>.Err("Mathematical geometry violation: Variance cannot be negative");
            }
            
            // Logarithmic fallout penalty
            double penalty = Math.Log10(epistemicVariance + 1.0);
            return Result<double>.Ok(penalty);
        }
    }
}
