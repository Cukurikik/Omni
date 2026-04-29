using System;

namespace Omni.Business.EnvoyProxy
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class HealthCheck
    {
        public OmniResult<bool> EvaluateUpstreamHealth(int consecutive_failures, int failure_threshold)
        {
            if (failure_threshold <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Failure threshold must be strictly positive"));
            }

            if (consecutive_failures < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Consecutive failures cannot be negative"));
            }

            // Business rule: Eject outlier if failures exceed or equal threshold
            bool is_healthy = consecutive_failures < failure_threshold;

            return new OmniResult<bool>(is_healthy);
        }
    }
}
