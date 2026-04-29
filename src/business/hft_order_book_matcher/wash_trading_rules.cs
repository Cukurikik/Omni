using System;

namespace Omni.Business.HftOrderBookMatcher
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class WashTradingRules
    {
        public OmniResult<bool> IsTradeAllowed(string buyer_id, string seller_id)
        {
            if (string.IsNullOrEmpty(buyer_id) || string.IsNullOrEmpty(seller_id))
            {
                return new OmniResult<bool>(new ArgumentException("Trader IDs cannot be empty"));
            }

            // Financial Compliance Logic: Wash Trading Prevention
            // It is illegal for an entity to trade with itself to artificially inflate volume.
            // The exchange matching engine MUST reject these orders before execution.
            
            if (buyer_id == seller_id)
            {
                return new OmniResult<bool>(false); // Reject trade
            }
            
            return new OmniResult<bool>(true); // Allow trade
        }
    }
}
