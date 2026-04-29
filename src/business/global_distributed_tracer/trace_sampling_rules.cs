using System;

namespace Omni.Business.GlobalDistributedTracer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class TraceSamplingRules
    {
        public OmniResult<bool> ShouldSampleRequest(bool is_error, double current_qps)
        {
            if (current_qps < 0)
            {
                return new OmniResult<bool>(new ArgumentException("QPS cannot be negative"));
            }

            // Distributed Tracing Business Logic: Adaptive Sampling
            // Logging 100% of traces at 100,000 QPS will crash the logging database (and cost millions).
            // We must drop successful requests dynamically but ALWAYS keep error traces.
            
            if (is_error)
            {
                // Always log errors, 100% sampling rate
                return new OmniResult<bool>(true);
            }
            
            if (current_qps > 10000)
            {
                // Extremely high load: 1% sampling rate
                return new OmniResult<bool>(false); // Simulate skipping
            }
            else if (current_qps > 1000)
            {
                // Moderate load: 10% sampling rate
                return new OmniResult<bool>(false);
            }
            
            // Low load: 100% sampling rate
            return new OmniResult<bool>(true);
        }
    }
}
