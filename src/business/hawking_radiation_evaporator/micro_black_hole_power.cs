using System;

namespace Omni.Business.HawkingRadiationEvaporator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class MicroBlackHolePower
    {
        public OmniResult<string> EvaluateEvaporationYield(double black_hole_mass_kg, double power_output_watts)
        {
            if (black_hole_mass_kg <= 0)
            {
                return new OmniResult<string>(new ArgumentException("Mass must be positive"));
            }

            // Power Generation Business Logic: Hawking Evaporator
            // We use a micro-black hole (roughly the mass of a mountain) as the ultimate battery.
            // As it evaporates via Hawking Radiation, it emits pure gamma rays which we capture for power.
            // WARNING: As it shrinks, the power output grows exponentially. In the final milliseconds,
            // it detonates with the force of millions of nuclear bombs. We must feed it matter
            // to keep the mass perfectly stable.
            
            double critical_mass_threshold = 1.0e8; // 100,000 tons
            
            if (black_hole_mass_kg < critical_mass_threshold)
            {
                return new OmniResult<string>("CRITICAL_EVAPORATION_WARNING: Black hole mass approaching terminal flash point. Inject asteroid matter immediately to cool the horizon.");
            }
            
            return new OmniResult<string>("STABLE_YIELD: Evaporation rate steady. Power extraction nominal.");
        }
    }
}
