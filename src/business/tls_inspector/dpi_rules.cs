using System;
using System.Collections.Generic;

namespace Omni.Business.TlsInspector
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class DpiRules
    {
        public OmniResult<bool> ValidateSNI(string sni_hostname, List<string> blocked_domains)
        {
            if (string.IsNullOrEmpty(sni_hostname))
            {
                 // ESNI (Encrypted SNI) or ECH (Encrypted Client Hello) might be in use, or plain IP
                 return new OmniResult<bool>(new InvalidOperationException("SNI is missing or encrypted (ECH)"));
            }

            // Simple strict domain blocking logic
            foreach (var blocked in blocked_domains)
            {
                if (sni_hostname.EndsWith(blocked, StringComparison.OrdinalIgnoreCase))
                {
                    return new OmniResult<bool>(new InvalidOperationException($"DPI Blocked: SNI '{sni_hostname}' matches blacklist policy '{blocked}'."));
                }
            }

            return new OmniResult<bool>(true);
        }
    }
}
