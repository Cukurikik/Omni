using System;

namespace Omni.Business.ResponsibleAiAuditor
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class BiasThresholds
    {
        public OmniResult<string> EvaluateModelFairness(double disparate_impact_ratio)
        {
            if (disparate_impact_ratio < 0.0)
            {
                return new OmniResult<string>(new ArgumentException("Impact ratio cannot be negative"));
            }

            // Responsible AI Business Logic: 80% Rule (Four-Fifths Rule)
            // US EEOC guidelines state that selection rate for any group less than 4/5 (0.8) 
            // of the highest group is evidence of adverse impact.
            
            if (disparate_impact_ratio < 0.8)
            {
                return new OmniResult<string>("FAIL_ADVERSE_IMPACT_DETECTED");
            }
            
            // Over-selection (reverse bias) check
            if (disparate_impact_ratio > 1.25)
            {
                return new OmniResult<string>("FAIL_REVERSE_BIAS_DETECTED");
            }

            return new OmniResult<string>("PASS_FAIRNESS_CHECK");
        }
    }
}
