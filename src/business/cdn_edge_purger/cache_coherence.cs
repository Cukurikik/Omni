using System;

namespace Omni.Business.CdnEdgePurger
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CacheCoherence
    {
        public OmniResult<bool> ShouldPurgeGlobal(bool is_critical_security_patch, double time_since_last_purge_sec)
        {
            if (time_since_last_purge_sec < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Time cannot be negative"));
            }

            // CDN Business Logic: Cache Coherence & Purge Limits
            // Purging the entire global CDN (Cloudflare/Fastly) instantly causes a massive
            // thundering herd attack on the origin servers. It must be strictly regulated.
            
            if (is_critical_security_patch)
            {
                // Override all limits for security patches (e.g. leaked keys in JS bundle)
                return new OmniResult<bool>(true);
            }
            
            if (time_since_last_purge_sec < 300)
            {
                // Rate limit: Do not allow full global purges more than once every 5 minutes
                // to protect the origin database from melting.
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
