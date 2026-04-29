using System;

namespace Omni.Business.ExoplanetBiosignatureSpectrometer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class DrakeEquation
    {
        public OmniResult<bool> IsBiosignatureSignificant(double methane_ppm, double oxygen_ppm, double habitability_index)
        {
            if (methane_ppm < 0 || oxygen_ppm < 0 || habitability_index < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Concentrations must be positive"));
            }

            // Astrobiology Business Logic: Atmospheric Disequilibrium
            // Finding Oxygen OR Methane is interesting. Finding them TOGETHER is a massive
            // biosignature, because they react and destroy each other quickly.
            // If they are both present in high quantities, something (life) must be continuously producing them.
            
            if (methane_ppm > 1.5 && oxygen_ppm > 200000.0 && habitability_index > 0.8)
            {
                return new OmniResult<bool>(true); // Extreme biosignature detected. Trigger global telescope array.
            }
            
            return new OmniResult<bool>(false); // Normal dead rock or gas giant.
        }
    }
}
