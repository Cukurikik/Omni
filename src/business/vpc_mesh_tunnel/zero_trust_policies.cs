using System;

namespace Omni.Business.VpcMeshTunnel
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ZeroTrustPolicies
    {
        public OmniResult<bool> IsConnectionAllowed(string source_vpc_id, string target_vpc_id, bool has_explicit_grant)
        {
            if (string.IsNullOrEmpty(source_vpc_id) || string.IsNullOrEmpty(target_vpc_id))
            {
                return new OmniResult<bool>(new ArgumentException("VPC IDs cannot be empty"));
            }

            // VPC Mesh Business Logic: Zero-Trust Network Architecture
            // In a modern multi-cloud setup, implicit trust is eliminated.
            // Even if two VPCs are in the same account, they cannot communicate unless explicitly granted via IAM/Mesh policy.
            
            if (!has_explicit_grant)
            {
                // DENY BY DEFAULT. No implicit trust.
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
