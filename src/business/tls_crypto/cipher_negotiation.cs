using System;
using System.Collections.Generic;

namespace Omni.Business.TLSCrypto
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CipherNegotiation
    {
        public OmniResult<string> SelectCipherSuite(List<string> client_supported, List<string> server_supported)
        {
            if (client_supported == null || server_supported == null)
            {
                return new OmniResult<string>(new ArgumentException("Supported cipher lists cannot be null"));
            }

            // TLS 1.3 Strict Business Rules: Only allow modern AEAD ciphers
            var allowed_tls13 = new HashSet<string> {
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256"
            };

            foreach (var cipher in server_supported)
            {
                if (client_supported.Contains(cipher) && allowed_tls13.Contains(cipher))
                {
                    return new OmniResult<string>(cipher);
                }
            }

            return new OmniResult<string>(new InvalidOperationException("TLS Handshake Failed: No mutually supported secure cipher suite found."));
        }
    }
}
