using System;

namespace Omni.Business.MarketMakerSpreadCalc
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class PositionLimits
    {
        public OmniResult<bool> CanProvideLiquidity(int current_inventory, int max_inventory_limit)
        {
            if (max_inventory_limit <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Limit must be positive"));
            }

            // Market Making Business Logic: Inventory Risk Limits
            // A market maker provides liquidity on both sides, but if the market crashes, 
            // they can get "run over" and accumulate massive toxic inventory.
            // Hard limits stop quoting when inventory becomes too heavily skewed.
            
            if (Math.Abs(current_inventory) >= max_inventory_limit)
            {
                return new OmniResult<bool>(false); // Skew is too high, halt quoting on one side
            }
            
            return new OmniResult<bool>(true); // Nominal, continue quoting
        }
    }
}
