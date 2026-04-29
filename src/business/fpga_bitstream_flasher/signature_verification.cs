using System;

namespace Omni.Business.FpgaBitstreamFlasher
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SignatureVerification
    {
        public OmniResult<bool> IsBitstreamAuthorized(string expected_hash, string actual_hash, bool is_production)
        {
            if (string.IsNullOrEmpty(expected_hash) || string.IsNullOrEmpty(actual_hash))
            {
                return new OmniResult<bool>(new ArgumentException("Hashes cannot be empty"));
            }

            // FPGA Business Logic: Bitstream Security
            // Prevents malicious actors from flashing malicious hardware logic onto OMNI Edge devices
            
            if (expected_hash != actual_hash)
            {
                // In production, mismatched hashes are strictly rejected
                if (is_production)
                {
                    return new OmniResult<bool>(false);
                }
                else
                {
                    // In dev mode, we might allow it (or flag a warning)
                    // But for strict OMNI rules, we reject it anyway
                    return new OmniResult<bool>(false);
                }
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
