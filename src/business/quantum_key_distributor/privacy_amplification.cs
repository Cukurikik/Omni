using System;

namespace Omni.Business.QuantumKeyDistributor
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class PrivacyAmplification
    {
        public OmniResult<bool> IsKeySecure(double quantum_bit_error_rate, double max_qber_threshold)
        {
            if (quantum_bit_error_rate < 0 || max_qber_threshold <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Rates must be positive"));
            }

            // Quantum Cryptography Business Logic: Eavesdropper Detection
            // According to quantum mechanics (No-Cloning Theorem), if an eavesdropper (Eve)
            // intercepts the photons, she irrevocably alters their state, causing the Quantum Bit Error Rate (QBER) to spike.
            
            if (quantum_bit_error_rate > max_qber_threshold)
            {
                return new OmniResult<bool>(false); // Eve is listening. Discard the key.
            }
            
            return new OmniResult<bool>(true); // Key is secure. Proceed to Privacy Amplification hashing.
        }
    }
}
