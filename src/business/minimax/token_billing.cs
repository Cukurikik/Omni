using System;

namespace Omni.MiniMax
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk => string.IsNullOrEmpty(Error);
    }

    public class TokenBilling
    {
        public OmniResult<decimal> CalculateTokenCost(int promptTokens, int completionTokens, decimal ratePerThousand)
        {
            if (promptTokens < 0 || completionTokens < 0)
            {
                return new OmniResult<decimal> { Error = "Token counts cannot be negative" };
            }

            // Enterprise C# domain logic for MiniMax token billing
            decimal totalTokens = promptTokens + completionTokens;
            decimal cost = (totalTokens / 1000m) * ratePerThousand;

            return new OmniResult<decimal> { Value = cost };
        }
    }
}
