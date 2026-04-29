using System;

namespace Omni.Business.TimeSeriesForecaster
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class AnomalyThresholds
    {
        public OmniResult<bool> EvaluateLLMPrediction(double predicted_value, double historical_mean, double historical_std)
        {
            if (historical_std <= 0.0)
            {
                return new OmniResult<bool>(new ArgumentException("Standard deviation must be positive"));
            }

            // Time-Series Business Logic: LLM Safety Bounds
            // LLMs are notoriously bad at pure math. If the LLM predicts a time-series value
            // that is wildly outside historical norms (> 5 Sigma), flag it as a hallucination.
            
            double z_score = Math.Abs((predicted_value - historical_mean) / historical_std);
            
            if (z_score > 5.0)
            {
                // Likely an LLM hallucination, do not trust this forecast
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
