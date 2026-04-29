using System;

namespace Omni.Business.KinematicTrajectoryPlanner
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class JointLimits
    {
        public OmniResult<bool> IsVelocitySafe(double current_joint_velocity_rad_s, double max_safe_velocity_rad_s)
        {
            if (max_safe_velocity_rad_s <= 0.0)
            {
                return new OmniResult<bool>(new ArgumentException("Max velocity must be positive"));
            }

            // Kinematic Business Logic: Physical Safety Constraints
            // If a robotic arm joint spins too fast, it can destroy the gearbox, tear cables, 
            // or fatally injure humans in the vicinity (Cobot safety standards).
            
            double abs_velocity = Math.Abs(current_joint_velocity_rad_s);
            
            if (abs_velocity > max_safe_velocity_rad_s)
            {
                // Unsafe velocity detected. The trajectory MUST be aborted or clamped.
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
