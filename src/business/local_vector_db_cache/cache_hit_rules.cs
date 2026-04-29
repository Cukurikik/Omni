using System;

namespace Omni.Business.LocalVectorDbCache
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CacheHitRules
    {
        public OmniResult<bool> ShouldFetchFromCloud(double current_cache_hit_ratio)
        {
            if (current_cache_hit_ratio < 0.0 || current_cache_hit_ratio > 1.0)
            {
                return new OmniResult<bool>(new ArgumentException("Hit ratio must be between 0.0 and 1.0"));
            }

            // Local Vector DB Business Logic: Pre-fetching Triggers
            // If the local Edge cache is missing queries too often, trigger a bulk pre-fetch from the Cloud DB
            
            if (current_cache_hit_ratio < 0.3)
            {
                // Less than 30% hit rate means the local device has the wrong domain context loaded
                // Trigger cloud fetch
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(false);
        }
    }
}
