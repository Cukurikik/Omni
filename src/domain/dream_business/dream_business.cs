using System;

namespace Omni.Semester13.Batch07.DreamBusiness
{
    public class DreamPolicyError : Exception
    {
        public DreamPolicyError(string msg) : base(msg) {}
    }

    public class Result<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public Result(T value) { Value = value; }
        public Result(Exception error) { Error = error; }

        public T Unwrap() {
            if (!IsOk) throw Error;
            return Value;
        }
    }

    /// <summary>
    /// OMNI Engine: dream-business
    /// Domain logic for validating generated image properties against business guidelines.
    /// </summary>
    public class DreamBusinessEngine
    {
        private readonly double _maxMaskDensityTax;

        public DreamBusinessEngine(double maxMaskDensityTax = 0.5)
        {
            _maxMaskDensityTax = maxMaskDensityTax;
        }

        public Result<double> EvaluateGenerationTax(double maskDensity, double generationTimeSecs)
        {
            try
            {
                if (maskDensity < 0 || maskDensity > 1)
                    return new Result<double>(new DreamPolicyError("Density parameter geometrically invalid"));

                if (generationTimeSecs <= 0)
                    return new Result<double>(new DreamPolicyError("Time cannot be mathematically zero or negative"));

                // Business logic: High density + long time = higher compute tax
                double baseRate = 1.0;
                double densityPenalty = maskDensity * _maxMaskDensityTax;
                double timePenalty = Math.Log10(generationTimeSecs + 1) * 0.2;

                double totalTaxRate = baseRate + densityPenalty + timePenalty;

                return new Result<double>(totalTaxRate);
            }
            catch (Exception ex)
            {
                return new Result<double>(new DreamPolicyError($"Tax computation failed: {ex.Message}"));
            }
        }

        public Result<bool> ValidatePromptGuidance(double promptDivergence)
        {
             try
             {
                  if (promptDivergence < 0.0) return new Result<bool>(new DreamPolicyError("Negative divergence is mathematically illogical."));
                  
                  // Business rule: if it diverged too much, reject it.
                  bool isValid = promptDivergence <= 2.5;
                  
                  return new Result<bool>(isValid);
             }
             catch (Exception ex)
             {
                  return new Result<bool>(new DreamPolicyError($"Guidance mapping failed: {ex.Message}"));
             }
        }
    }
}
