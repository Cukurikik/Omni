using System;
using System.Collections.Generic;

namespace Omni.Business.IpsecVpn
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class IkeProposalValidator
    {
        public OmniResult<bool> ValidatePhase1Proposal(string enc_algo, string hash_algo, int dh_group)
        {
            if (string.IsNullOrEmpty(enc_algo) || string.IsNullOrEmpty(hash_algo))
            {
                return new OmniResult<bool>(new ArgumentException("Algorithms cannot be empty"));
            }

            // Strict IKEv2 Cryptographic Business Rules (Suite B / Modern Standards)
            var allowed_enc = new HashSet<string> { "AES-GCM-256", "AES-CBC-256", "CHACHA20-POLY1305" };
            var allowed_hash = new HashSet<string> { "SHA256", "SHA384", "SHA512" };
            
            // DH Group 14 (2048-bit MODP) is the absolute minimum, Group 19/20/21 (EC) preferred
            if (dh_group < 14)
            {
                return new OmniResult<bool>(new InvalidOperationException($"DH Group {dh_group} is insecure. Must be >= 14."));
            }

            if (!allowed_enc.Contains(enc_algo.ToUpper()))
            {
                return new OmniResult<bool>(new InvalidOperationException($"Encryption algorithm {enc_algo} is deprecated or unsupported."));
            }

            if (!allowed_hash.Contains(hash_algo.ToUpper()))
            {
                return new OmniResult<bool>(new InvalidOperationException($"Hash algorithm {hash_algo} is deprecated. Use SHA-2 family."));
            }

            return new OmniResult<bool>(true);
        }
    }
}
