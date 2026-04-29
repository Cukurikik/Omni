using System;

namespace Omni.Business.KafkaBroker
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class RetentionSla
    {
        public OmniResult<bool> ShouldRetainSegment(long segment_age_ms, long max_retention_ms, long segment_size_bytes, long max_retention_bytes)
        {
            if (max_retention_ms <= 0 && max_retention_bytes <= 0)
            {
                // Infinite retention
                return new OmniResult<bool>(true);
            }

            // Kafka Business Rule: Log retention based on time or size, whichever hits first
            if (max_retention_ms > 0 && segment_age_ms > max_retention_ms)
            {
                return new OmniResult<bool>(false); // Delete, too old
            }

            if (max_retention_bytes > 0 && segment_size_bytes > max_retention_bytes)
            {
                return new OmniResult<bool>(false); // Delete, too large
            }

            return new OmniResult<bool>(true); // Retain
        }
    }
}
