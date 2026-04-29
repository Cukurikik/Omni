using System;

namespace Omni.Business.ShapExplainer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CoalitionRules
    {
        public OmniResult<bool> ValidateGameTheoryBounds(double[] expected_values, double base_value, double model_output, double tolerance = 1e-4)
        {
            if (expected_values == null)
            {
                return new OmniResult<bool>(new ArgumentException("Expected values array cannot be null"));
            }

            // Efficiency property constraint: 
            // The sum of Shapley values must equal the difference between model output and base value.
            double sum_shap = 0.0;
            for (int i = 0; i < expected_values.Length; i++)
            {
                sum_shap += expected_values[i];
            }

            double difference = model_output - base_value;

            if (Math.Abs(sum_shap - difference) > tolerance)
            {
                return new OmniResult<bool>(new InvalidOperationException($"Efficiency property violated. Sum of SHAP values ({sum_shap}) does not match output difference ({difference}) within tolerance."));
            }

            return new OmniResult<bool>(true);
        }
    }
}
