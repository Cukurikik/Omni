using System;

namespace Omni.Business.LongMem
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk => string.IsNullOrEmpty(Error);
    }

    public class MemoryLifecycleManager
    {
        public OmniResult<bool> EvictStaleMemory(string sessionId, DateTime threshold)
        {
            if (string.IsNullOrEmpty(sessionId))
            {
                return new OmniResult<bool> { Value = false, Error = "Session ID cannot be null" };
            }

            // Domain logic for evicting old memories
            bool evicted = DateTime.UtcNow > threshold;
            return new OmniResult<bool> { Value = evicted, Error = null };
        }
    }
}
