using System;
using System.Collections.Generic;

namespace Omni.Business.WireGuardTun
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CryptokeyRouting
    {
        public OmniResult<bool> ValidateAllowedIPs(string source_ip, List<string> peer_allowed_ips)
        {
            if (string.IsNullOrEmpty(source_ip))
            {
                return new OmniResult<bool>(new ArgumentException("Source IP cannot be empty"));
            }

            if (peer_allowed_ips == null || peer_allowed_ips.Count == 0)
            {
                return new OmniResult<bool>(new InvalidOperationException("Peer has no AllowedIPs configured, routing denied"));
            }

            // Simplified exact match for Zero Mock. 
            // In a full implementation, this evaluates CIDR subnet masking.
            bool is_allowed = peer_allowed_ips.Contains(source_ip) || peer_allowed_ips.Contains("0.0.0.0/0");

            if (!is_allowed)
            {
                return new OmniResult<bool>(new InvalidOperationException($"Cryptokey Routing violation: {source_ip} is not in peer's AllowedIPs"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
