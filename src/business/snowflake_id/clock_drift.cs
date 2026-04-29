using System;

namespace Omni.Business.SnowflakeID
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ClockDriftRules
    {
        public OmniResult<bool> ValidateMonotonicTime(long current_time_ms, long last_time_ms)
        {
            // Business rule: NTP clock drift causing time to move backwards destroys uniqueness guarantees
            
            if (current_time_ms < last_time_ms)
            {
                long drift = last_time_ms - current_time_ms;
                return new OmniResult<bool>(new InvalidOperationException($"Clock moved backwards by {drift}ms. Rejecting ID generation until time catches up."));
            }

            return new OmniResult<bool>(true);
        }
    }
}
