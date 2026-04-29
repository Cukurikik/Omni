using System;

namespace Omni.Business.HyperspatialNavigationMatrix
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class LightConeViolation
    {
        public OmniResult<string> EvaluateCausalityPreservation(double target_distance_lightyears, double warp_velocity_c)
        {
            if (target_distance_lightyears < 0 || warp_velocity_c < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid astrogation vectors"));
            }

            // Astrogation Business Logic: Causality Preservation
            // Traveling faster than light allows you to outrun light itself. Depending on
            // your reference frame, you could arrive before you left, violating causality.
            // We must limit warp trajectories to prevent Closed Timelike Curves (CTCs).
            
            if (warp_velocity_c > 10.0)
            {
                // Arbitrary safety limit to prevent extreme temporal paradoxes
                return new OmniResult<string>("CAUSALITY_VIOLATION_RISK: Warp factor exceeds safe limit (10c). Trajectory intersects with past light cones. Aborting jump.");
            }
            
            if (target_distance_lightyears > 100000.0)
            {
                 return new OmniResult<string>("OUT_OF_BOUNDS: Target exceeds galactic rim. Astrometric data insufficient to plot safe warp tunnel.");
            }
            
            return new OmniResult<string>("ASTROGATION_LOCK: Trajectory secure. Light cone preserved. Spooling exotic matter injectors.");
        }
    }
}
