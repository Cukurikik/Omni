using System;

namespace Omni.Semester13.Batch09.PegasusPricing
{
    public class PegasusPricingError : Exception
    {
        public PegasusPricingError(string msg) : base(msg) {}
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
    /// OMNI Engine: pegasus-pricing
    /// Dynamic pricing mapped to the hyperdimensional token density required by universal embeddings.
    /// </summary>
    public class PegasusPricingEngine
    {
        private readonly double _baseDimensionalPrice;

        public PegasusPricingEngine(double basePrice = 0.005)
        {
            _baseDimensionalPrice = basePrice;
        }

        public Result<double> CalculateMultimodalEmbeddingCost(double effectiveDensity, bool isLossy)
        {
            try
            {
                if (effectiveDensity < 0.0)
                    return new Result<double>(new PegasusPricingError("Token density inherently void for cost basis"));

                double finalCost = effectiveDensity * _baseDimensionalPrice;
                
                // If it is lossy, we discount the final cost since precision was reduced
                if (isLossy) {
                     finalCost *= 0.5;
                }

                return new Result<double>(finalCost);
            }
            catch (Exception ex)
            {
                return new Result<double>(new PegasusPricingError($"Dimensional scaling crashed pricing constraints: {ex.Message}"));
            }
        }
    }
}
