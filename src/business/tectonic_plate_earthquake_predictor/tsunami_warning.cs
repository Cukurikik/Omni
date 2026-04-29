using System;

namespace Omni.Business.TectonicPlateEarthquakePredictor
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class TsunamiWarning
    {
        public OmniResult<string> EvaluateTsunamiThreat(double earthquake_magnitude_richter, bool is_epicenter_under_ocean, double focal_depth_km)
        {
            if (earthquake_magnitude_richter < 0 || focal_depth_km < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid geological parameters"));
            }

            // Disaster Management Business Logic: Tsunami Warning Trigger
            // A tsunami is only generated if a massive earthquake (usually > 7.5) occurs UNDER THE OCEAN,
            // and is SHALLOW enough to physically displace the sea floor. Deep earthquakes don't cause tsunamis.
            
            if (earthquake_magnitude_richter >= 7.5 && is_epicenter_under_ocean && focal_depth_km <= 50.0)
            {
                return new OmniResult<string>("TSUNAMI_WARNING_ISSUED: Massive shallow subsea displacement detected. Triggering coastal sirens.");
            }
            
            return new OmniResult<string>("NO_TSUNAMI_THREAT: Parameters do not support mass oceanic displacement.");
        }
    }
}
