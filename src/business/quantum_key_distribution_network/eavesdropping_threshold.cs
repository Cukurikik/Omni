using System;

namespace Omni.Business.QuantumKeyDistributionNetwork
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class EavesdroppingThreshold
    {
        public OmniResult<string> EvaluateChannelSecurity(double current_qber)
        {
            if (current_qber < 0 || current_qber > 1.0)
            {
                return new OmniResult<string>(new ArgumentException("QBER must be between 0 and 1"));
            }

            // Cryptographic Business Logic: Information-Theoretic Security
            // In BB84, a QBER of 0.11 (11%) is the theoretical maximum where Alice and Bob
            // can still use privacy amplification to distill a secure key.
            // A QBER of 0.25 (25%) means Eve is intercepting and resending every single photon.
            
            double secure_threshold = 0.11;
            
            if (current_qber > secure_threshold)
            {
                return new OmniResult<string>("EAVESDROPPING_DETECTED: QBER exceeds 11% threshold. The channel is compromised by a third party. Abort key generation.");
            }
            
            return new OmniResult<string>("CHANNEL_SECURE: QBER within acceptable limits. Proceed with privacy amplification and key distillation.");
        }
    }
}
