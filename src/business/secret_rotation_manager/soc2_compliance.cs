using System;

namespace Omni.Business.SecretRotationManager
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class Soc2Compliance
    {
        public OmniResult<bool> IsRotationRequired(int days_since_last_rotation, bool is_production_db)
        {
            if (days_since_last_rotation < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Days cannot be negative"));
            }

            // Security Business Logic: SOC2 and PCI-DSS Compliance
            // Enterprise rules dictate strict hard-limits on how long a credential can live.
            
            int max_days = is_production_db ? 30 : 90;
            
            if (days_since_last_rotation >= max_days)
            {
                // Key has expired its compliance TTL. Must rotate instantly.
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(false);
        }
    }
}
