using System;

namespace Omni.Business.NeutronStarPulsarNavigation
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class GalacticGPS
    {
        public OmniResult<string> EvaluateTriangulationLock(int locked_pulsars_count, double positional_uncertainty_meters)
        {
            if (locked_pulsars_count < 0 || positional_uncertainty_meters < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid navigation metrics"));
            }

            // Navigation Business Logic: Galactic Positioning System (GPS)
            // Just like Earth GPS requires 4 satellites for a 3D position + Time lock,
            // deep space navigation requires phase-locking onto at least 4 millisecond pulsars.
            // If we don't have a lock, initiating a warp jump could embed the ship inside a star.
            
            if (locked_pulsars_count < 4)
            {
                return new OmniResult<string>($"INSUFFICIENT_TELEMETRY: Only {locked_pulsars_count}/4 pulsars locked. Warp drive locked out. Blind jumping is fatal.");
            }
            
            if (positional_uncertainty_meters > 5000.0) // 5km uncertainty
            {
                return new OmniResult<string>("HIGH_UNCERTAINTY: Positional error too large. Wait for ISM dispersion correction to converge.");
            }
            
            return new OmniResult<string>("GALACTIC_LOCK_ACHIEVED: Starship position absolute. Warp vector calculation authorized.");
        }
    }
}
