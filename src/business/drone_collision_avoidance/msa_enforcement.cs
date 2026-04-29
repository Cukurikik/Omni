using System;

namespace Omni.Business.DroneCollisionAvoidance
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class MsaEnforcement
    {
        public OmniResult<bool> IsAltitudeSafe(double current_altitude_meters, double msa_meters)
        {
            if (current_altitude_meters < 0 || msa_meters <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Altitudes must be positive"));
            }

            // Aviation Business Logic: Minimum Safe Altitude (MSA)
            // Regardless of collision avoidance logic, the drone MUST NEVER drop below the MSA
            // (e.g., to avoid power lines or buildings). If an avoidance maneuver suggests dropping
            // below MSA, the business layer vetoes it.
            
            if (current_altitude_meters < msa_meters)
            {
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
