using System;

namespace Omni.Business.CryptoWalletHsmSigner
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class MultisigThreshold
    {
        public OmniResult<bool> IsTransactionAuthorized(int valid_signatures_collected, int threshold_required)
        {
            if (valid_signatures_collected < 0 || threshold_required <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Thresholds must be positive"));
            }

            // Wallet Business Logic: Multi-Signature (M-of-N) Authorization
            // Enterprise crypto treasuries require multiple hardware wallets to sign a transaction
            // (e.g., 3 out of 5 board members) before funds can be moved, preventing single-point-of-failure theft.
            
            if (valid_signatures_collected < threshold_required)
            {
                return new OmniResult<bool>(false); // Not enough signatures yet
            }
            
            return new OmniResult<bool>(true); // Quorum reached, broadcast to network
        }
    }
}
