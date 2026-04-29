using System;

namespace Omni.Business.SubmarineCableFaultLocator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class RepairDispatch
    {
        public OmniResult<string> DetermineRepairVessel(double fault_distance_km, double max_littoral_range_km)
        {
            if (fault_distance_km < 0 || max_littoral_range_km <= 0)
            {
                return new OmniResult<string>(new ArgumentException("Distances must be positive"));
            }

            // Infrastructure Logistics Logic: Subsea Cable Repair
            // If a fault is close to shore (littoral), a smaller local ship can fix it.
            // If it's deep in the middle of the Pacific Ocean, we must dispatch a massive Deep Sea Repair Vessel.
            
            if (fault_distance_km <= max_littoral_range_km)
            {
                return new OmniResult<string>("DISPATCH_LITTORAL_VESSEL: Fault is within shallow water shelf.");
            }
            
            return new OmniResult<string>("DISPATCH_DEEP_SEA_VESSEL: Fault requires ROV (Remotely Operated Vehicle) operations.");
        }
    }
}
