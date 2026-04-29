using System;

namespace Omni.Business.DarkMatterAxionDetector
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class DiscoveryThreshold
    {
        public OmniResult<string> EvaluateStatisticalSignificance(double signal_to_noise_ratio, double p_value)
        {
            if (signal_to_noise_ratio < 0 || p_value < 0 || p_value > 1.0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid statistical parameters"));
            }

            // Particle Physics Business Logic: 5-Sigma Discovery Standard
            // In physics, you cannot claim a discovery (like Dark Matter) unless your signal
            // is 5 standard deviations (5-sigma) above background noise. That's a p-value of 3 x 10^-7.
            // A 3-sigma signal is just an "observation" or "hint".
            
            double five_sigma_p_value = 0.0000003;
            
            if (p_value <= five_sigma_p_value)
            {
                return new OmniResult<string>("NOBEL_PRIZE_DISCOVERY: Axion dark matter confirmed at 5-sigma significance.");
            }
            else if (p_value <= 0.0013) // 3-sigma
            {
                return new OmniResult<string>("STRONG_HINT: 3-sigma excess detected. Need more data integration time.");
            }
            
            return new OmniResult<string>("BACKGROUND_NOISE: Consistent with Standard Model background. Keep scanning.");
        }
    }
}
