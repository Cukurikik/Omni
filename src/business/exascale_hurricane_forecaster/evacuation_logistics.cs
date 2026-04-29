using System;

namespace Omni.Business.ExascaleHurricaneForecaster
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class EvacuationLogistics
    {
        public OmniResult<string> DetermineEvacuationZones(double predicted_storm_surge_meters, double coastal_elevation_meters)
        {
            if (predicted_storm_surge_meters < 0 || coastal_elevation_meters < 0)
            {
                return new OmniResult<string>(new ArgumentException("Meters must be positive"));
            }

            // Emergency Management Business Logic: Mandatory Evacuation
            // If the supercomputer predicts a storm surge that exceeds the elevation of a coastal city,
            // we must immediately trigger FEMA protocols and reverse the highways for mass evacuation.
            
            if (predicted_storm_surge_meters > coastal_elevation_meters)
            {
                return new OmniResult<string>("MANDATORY_EVACUATION: Storm surge will breach coastal defenses. Initiate contraflow traffic routing.");
            }
            
            return new OmniResult<string>("VOLUNTARY_EVACUATION: Surge remains below critical elevation. Shelter in place advised for inland residents.");
        }
    }
}
