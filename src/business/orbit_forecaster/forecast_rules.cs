using System;

namespace Omni.Business.OrbitForecaster
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ForecastRules
    {
        private readonly double _maxAllowedVariance;

        public ForecastRules(double maxAllowedVariance = 1000.0)
        {
            _maxAllowedVariance = maxAllowedVariance;
        }

        public OmniResult<ForecastBounds> ValidateForecast(double mean, double stdDev)
        {
            if (stdDev < 0)
            {
                return new OmniResult<ForecastBounds>(new ArgumentException("Standard deviation cannot be negative"));
            }

            double variance = stdDev * stdDev;
            if (variance > _maxAllowedVariance)
            {
                return new OmniResult<ForecastBounds>(new InvalidOperationException($"Variance {variance} exceeds safety threshold {_maxAllowedVariance}. Forecast too uncertain."));
            }

            // Calculate 95% confidence interval bounds deterministically (approx 1.96 std dev)
            double lowerBound = mean - (1.96 * stdDev);
            double upperBound = mean + (1.96 * stdDev);

            // Business constraint: Forecasts cannot project negative values for physical inventory/pricing
            lowerBound = Math.Max(0, lowerBound);
            mean = Math.Max(0, mean);

            return new OmniResult<ForecastBounds>(new ForecastBounds
            {
                Mean = mean,
                LowerBound95 = lowerBound,
                UpperBound95 = upperBound
            });
        }
    }

    public class ForecastBounds
    {
        public double Mean { get; set; }
        public double LowerBound95 { get; set; }
        public double UpperBound95 { get; set; }
    }
}
