using System;

namespace Omni.Business.BlockchainMempoolSniper
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SandwichPrevention
    {
        public OmniResult<bool> AnalyzeSandwichAttack(double victim_slippage_tolerance_percent)
        {
            if (victim_slippage_tolerance_percent < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Tolerance cannot be negative"));
            }

            // MEV Business Logic: Sandwich Attack Analysis
            // A sandwich attack involves front-running a victim's buy order to pump the price,
            // and immediately back-running them to sell for a profit.
            // If the victim has a 0% slippage tolerance, the attack will fail (victim's tx reverts).
            
            if (victim_slippage_tolerance_percent == 0.0)
            {
                return new OmniResult<bool>(false); // Attack mathematically impossible
            }
            
            return new OmniResult<bool>(true); // Vulnerable to extraction
        }
    }
}
