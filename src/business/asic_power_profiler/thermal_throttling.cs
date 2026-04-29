using System;

namespace Omni.Business.AsicPowerProfiler
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ThermalThrottling
    {
        public OmniResult<bool> ShouldThrottle(double current_die_temp_c, double thermal_throttle_limit_c)
        {
            if (current_die_temp_c < 0.0 || thermal_throttle_limit_c <= 0.0)
            {
                return new OmniResult<bool>(new ArgumentException("Temperatures must be positive"));
            }

            // ASIC Business Logic: Hardware Protection
            // If the silicon die exceeds the safe thermal limit (e.g. 95°C), the system MUST 
            // throttle the clock speeds immediately to prevent permanent physical silicon damage.
            
            if (current_die_temp_c >= thermal_throttle_limit_c)
            {
                // Critical thermal event. Throttle required.
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(false);
        }
    }
}
