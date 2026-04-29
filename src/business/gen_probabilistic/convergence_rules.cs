using System;

namespace Omni.Business.GenProbabilistic
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ConvergenceRules
    {
        public OmniResult<bool> HasConverged(double effective_sample_size, int num_particles)
        {
            if (num_particles <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Number of particles must be greater than 0"));
            }

            // Business rule: Particle filter resampling is triggered when ESS drops below a threshold
            // typically 50% of total particles.
            double threshold = num_particles * 0.5;

            if (effective_sample_size < threshold)
            {
                return new OmniResult<bool>(false); // Has not converged, requires resampling
            }

            return new OmniResult<bool>(true); // Converged / Healthy particle diversity
        }
    }
}
