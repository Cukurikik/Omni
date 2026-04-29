using System;

namespace Omni.Business.RoboticSwarmConsensus
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CollisionRules
    {
        public OmniResult<bool> IsDistanceSafe(double closest_neighbor_distance_meters, double safe_radius_meters)
        {
            if (closest_neighbor_distance_meters < 0 || safe_radius_meters <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Distances must be positive"));
            }

            // Swarm Business Logic: Absolute Collision Prevention
            // Even if the Boids algorithm wants to move closer for Cohesion, 
            // the business layer strictly enforces a minimum physical separation boundary.
            
            if (closest_neighbor_distance_meters < safe_radius_meters)
            {
                // CRITICAL AVOIDANCE: Override flocking vectors and perform emergency repulse.
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
