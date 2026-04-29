using System;
using System.Linq;

namespace Omni.Business.FederatedLearningAggregator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class PrivacyClippingRules
    {
        public OmniResult<double[]> ClipGradients(double[] raw_gradients, double max_l2_norm)
        {
            if (raw_gradients == null || max_l2_norm <= 0.0)
            {
                return new OmniResult<double[]>(new ArgumentException("Invalid inputs for gradient clipping"));
            }

            // Federated Business Logic: Differential Privacy L2 Clipping
            // Prevents edge devices from contributing abnormally large gradients that could 
            // be reverse-engineered to expose user data (e.g. memorizing credit cards)
            
            double sum_sq = raw_gradients.Sum(g => g * g);
            double l2_norm = Math.Sqrt(sum_sq);
            
            if (l2_norm <= max_l2_norm)
            {
                // No clipping needed
                return new OmniResult<double[]>(raw_gradients);
            }
            
            // Clip gradients
            double scaling_factor = max_l2_norm / l2_norm;
            double[] clipped = raw_gradients.Select(g => g * scaling_factor).ToArray();
            
            return new OmniResult<double[]>(clipped);
        }
    }
}
