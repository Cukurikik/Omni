using System;

namespace Omni.Business.NerfRenderer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class LodRules
    {
        public OmniResult<int> CalculateSamplesPerRay(double camera_distance, bool is_fast_mode)
        {
            if (camera_distance < 0.0)
            {
                return new OmniResult<int>(new ArgumentException("Camera distance cannot be negative"));
            }

            // NeRF Level-of-Detail Business Logic
            // The further away the camera, the fewer samples we need along the ray to render an acceptable image
            int base_samples = 64;
            
            if (camera_distance > 100.0)
            {
                base_samples = 16;
            }
            else if (camera_distance > 50.0)
            {
                base_samples = 32;
            }

            if (is_fast_mode)
            {
                base_samples /= 2;
            }

            // Ensure minimum safety floor
            base_samples = Math.Max(8, base_samples);

            return new OmniResult<int>(base_samples);
        }
    }
}
