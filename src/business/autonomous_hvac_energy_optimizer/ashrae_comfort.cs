using System;

namespace Omni.Business.AutonomousHvacEnergyOptimizer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class AshraeComfort
    {
        public OmniResult<bool> IsComfortMaintained(double predicted_temp_c, double predicted_humidity_percent)
        {
            if (predicted_temp_c < 0 || predicted_humidity_percent < 0 || predicted_humidity_percent > 100)
            {
                return new OmniResult<bool>(new ArgumentException("Invalid environmental inputs"));
            }

            // Energy Management Business Logic: ASHRAE Standard 55
            // The AI wants to save money by turning off the AC. We must enforce strict bounds
            // so office workers don't freeze or sweat. 
            // Normal comfort zone: ~20-24C, 30-60% Humidity.
            
            if (predicted_temp_c < 19.5 || predicted_temp_c > 24.5)
            {
                return new OmniResult<bool>(false); // Temperature out of bounds
            }
            
            if (predicted_humidity_percent < 30.0 || predicted_humidity_percent > 60.0)
            {
                return new OmniResult<bool>(false); // Humidity out of bounds
            }
            
            return new OmniResult<bool>(true); // Predicted state is comfortable, proceed with energy savings.
        }
    }
}
