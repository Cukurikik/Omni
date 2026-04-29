using System;

namespace Omni.Business.KardashevTypeIiiEnergyGrid
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class GalacticLogistics
    {
        public OmniResult<string> EvaluatePowerDistribution(double energy_produced_yottawatts, int billions_of_stars_in_grid)
        {
            if (energy_produced_yottawatts < 0 || billions_of_stars_in_grid < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid grid parameters"));
            }

            // Infrastructure Business Logic: Galactic Power Logistics
            // A Type III civilization routes power from the central supermassive black hole
            // to hundreds of billions of star systems across a 100,000 lightyear wide grid.
            
            // Assume each star system needs at least 1 Yottawatt of power to function
            // (A Type II civilization level per star)
            double required_power_yw = billions_of_stars_in_grid * 1.0;
            
            if (energy_produced_yottawatts < required_power_yw)
            {
                return new OmniResult<string>("BROWN_OUT_WARNING: Quasar output insufficient for current galactic grid load. Trillions of civilizations experiencing power failure. Drop more mass into the accretion disk immediately.");
            }
            
            if (energy_produced_yottawatts > required_power_yw * 1.5)
            {
                 return new OmniResult<string>("GRID_OVERLOAD_WARNING: Quasar output exceeding grid capacity. Risk of micro-wormhole plasma cascade. Vent excess energy into intergalactic space.");
            }
            
            return new OmniResult<string>("GALACTIC_GRID_STABLE: Type III civilization power demands fully met. Accretion rate nominal.");
        }
    }
}
