using System;

namespace Omni.Business.PhotonicTensorCore
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ThermalDriftRules
    {
        public OmniResult<bool> RequiresCalibration(double current_temp_celsius, double baseline_temp_celsius)
        {
            if (current_temp_celsius < 0.0 || baseline_temp_celsius < 0.0)
            {
                return new OmniResult<bool>(new ArgumentException("Temperatures must be absolute/positive"));
            }

            // Photonic Business Logic: Thermal Drift Compensation
            // Silicon photonics are extremely sensitive to heat. A 1°C change alters the refractive index of the waveguides,
            // corrupting the analog AI matrix multiplication.
            
            double delta_t = Math.Abs(current_temp_celsius - baseline_temp_celsius);
            
            if (delta_t > 0.5)
            {
                // Drift > 0.5°C requires immediate halting of inference and recalibration of the phase shifters
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(false);
        }
    }
}
