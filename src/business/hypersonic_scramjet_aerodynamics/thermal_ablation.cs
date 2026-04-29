using System;

namespace Omni.Business.HypersonicScramjetAerodynamics
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ThermalAblation
    {
        public OmniResult<bool> IsAblationShieldIntact(double leading_edge_temp_c, double ablation_melting_point_c)
        {
            if (leading_edge_temp_c < -273.15 || ablation_melting_point_c < -273.15)
            {
                return new OmniResult<bool>(new ArgumentException("Temperatures cannot be below absolute zero"));
            }

            // Aerospace Engineering Business Logic: Thermal Ablation limits
            // At Mach 10, air friction heats the nose cone of the vehicle to over 2000°C.
            // If the temperature exceeds the melting point of the carbon-carbon composite ablation shield,
            // the vehicle will disintegrate in milliseconds.
            
            if (leading_edge_temp_c >= ablation_melting_point_c)
            {
                return new OmniResult<bool>(false); // Catastrophic thermal failure.
            }
            
            return new OmniResult<bool>(true); // Thermal protection system nominal.
        }
    }
}
