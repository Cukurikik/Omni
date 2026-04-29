using System;

namespace Omni.Business.GpuTensorAllocator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class MultiTenantRules
    {
        public OmniResult<bool> IsAllocationAllowed(double requested_mb, double user_quota_mb, double current_usage_mb, bool is_priority_user)
        {
            if (requested_mb <= 0 || user_quota_mb <= 0 || current_usage_mb < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Invalid allocation metrics"));
            }

            // GPU Business Logic: Multi-Tenant Hardware Sharing
            // Enforces strict VRAM slicing so one user's massive LLM doesn't crash another user's ML pipeline
            
            double projected_usage = current_usage_mb + requested_mb;
            
            if (projected_usage > user_quota_mb)
            {
                if (is_priority_user && (projected_usage <= user_quota_mb * 1.10))
                {
                    // VIP users get a 10% burst allowance over their hard quota
                    return new OmniResult<bool>(true);
                }
                
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
