using System;

namespace Omni.Business.RsaSigner
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class KeyValidation
    {
        public OmniResult<bool> ValidateKeyStrength(int key_size_bits)
        {
            // Business rule: RSA keys must be at least 2048 bits for modern security standards
            if (key_size_bits < 2048)
            {
                return new OmniResult<bool>(new InvalidOperationException($"RSA key size {key_size_bits} is too weak. Minimum 2048 bits required."));
            }

            // Reject unreasonably large keys that cause CPU DoS vulnerabilities during decryption
            if (key_size_bits > 8192)
            {
                 return new OmniResult<bool>(new InvalidOperationException($"RSA key size {key_size_bits} exceeds operational maximum (8192 bits)."));
            }

            return new OmniResult<bool>(true);
        }
    }
}
