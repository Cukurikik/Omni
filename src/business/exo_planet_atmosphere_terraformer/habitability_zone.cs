using System;

namespace Omni.Business.ExoPlanetAtmosphereTerraformer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class HabitabilityZone
    {
        public OmniResult<string> EvaluateLiquidWaterStability(double surface_temperature_kelvin, double atmospheric_pressure_atm)
        {
            if (surface_temperature_kelvin < 0 || atmospheric_pressure_atm < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid thermodynamic metrics"));
            }

            // Exobiology Business Logic: The Goldilocks Zone
            // For a planet to be habitable by humans, it needs liquid water on the surface.
            // This requires a specific temperature (273K - 373K) AND sufficient atmospheric
            // pressure (otherwise water sublimates directly from ice to vapor, like on Mars).
            
            // Armstrong limit: Pressure where water boils at body temperature (0.0618 atm)
            if (atmospheric_pressure_atm < 0.0618)
            {
                return new OmniResult<string>("HABITABILITY_FAIL: Pressure too low. Water will sublimate. Blood will boil at body temperature. Continue pumping Nitrogen/Oxygen.");
            }
            
            if (surface_temperature_kelvin < 273.15)
            {
                return new OmniResult<string>("HABITABILITY_FAIL: Temperature too low. Global ice age (Snowball Earth condition). Increase super-greenhouse gas production.");
            }
            
            if (surface_temperature_kelvin > 373.15)
            {
                 return new OmniResult<string>("HABITABILITY_FAIL: Temperature too high. Runaway greenhouse effect (Venus condition). Increase surface albedo or deploy solar shades.");
            }
            
            return new OmniResult<string>("HABITABILITY_ACHIEVED: Liquid water stable on surface. Biosphere seeding authorized.");
        }
    }
}
