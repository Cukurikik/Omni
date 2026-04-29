using System;

namespace Omni.Business.HydrogenStorageLlm
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SafetyThresholds
    {
        public OmniResult<string> EvaluateMaterialViability(double operating_temp_k, double operating_pressure_bar)
        {
            if (operating_temp_k <= 0.0 || operating_pressure_bar <= 0.0)
            {
                return new OmniResult<string>(new ArgumentException("Temperature and pressure must be positive"));
            }

            // Hydrogen Storage Business Logic: DOE (Department of Energy) Targets
            // Evaluating if a material proposed by the LLM is physically viable
            
            if (operating_pressure_bar > 700.0)
            {
                return new OmniResult<string>("REJECT_EXCEEDS_CRITICAL_PRESSURE");
            }
            
            if (operating_temp_k < 77.0) // Below liquid nitrogen
            {
                 return new OmniResult<string>("WARNING_REQUIRES_EXTREME_CRYOGENICS");
            }
            
            if (operating_temp_k > 373.0 && operating_pressure_bar < 10.0)
            {
                 return new OmniResult<string>("WARNING_HIGH_TEMP_DESORPTION_INEFFICIENT");
            }

            return new OmniResult<string>("VIABLE_MATERIAL_CANDIDATE");
        }
    }
}
