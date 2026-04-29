using System;

namespace Omni.Business.AnimeAnimator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class AnimationConstraints
    {
        // Business logic limits based on 2D mesh breaking points
        private const double MaxYaw = Math.PI / 3; // 60 degrees
        private const double MaxPitch = Math.PI / 4; // 45 degrees
        private const double MaxRoll = Math.PI / 4;

        public OmniResult<PoseParameters> ClampPose(double requestedYaw, double requestedPitch, double requestedRoll)
        {
            // Deterministic constraint validation
            double clampedYaw = Math.Clamp(requestedYaw, -MaxYaw, MaxYaw);
            double clampedPitch = Math.Clamp(requestedPitch, -MaxPitch, MaxPitch);
            double clampedRoll = Math.Clamp(requestedRoll, -MaxRoll, MaxRoll);

            bool wasRestricted = (clampedYaw != requestedYaw) || 
                                 (clampedPitch != requestedPitch) || 
                                 (clampedRoll != requestedRoll);

            var pose = new PoseParameters
            {
                Yaw = clampedYaw,
                Pitch = clampedPitch,
                Roll = clampedRoll,
                Restricted = wasRestricted
            };

            return new OmniResult<PoseParameters>(pose);
        }
    }

    public class PoseParameters
    {
        public double Yaw { get; set; }
        public double Pitch { get; set; }
        public double Roll { get; set; }
        public bool Restricted { get; set; }
    }
}
