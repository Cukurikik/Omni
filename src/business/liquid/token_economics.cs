using System;

namespace Omni.Liquid
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk => string.IsNullOrEmpty(Error);
    }

    public class TokenEconomics
    {
        public OmniResult<decimal> CalculateComputeCost(int tokenCount, bool isMultimodal)
        {
            if (tokenCount <= 0)
            {
                return new OmniResult<decimal> { Error = "Token count must be positive" };
            }

            // Enterprise C# logic for Liquid unified token economics
            decimal baseRate = 0.0001m;
            decimal multiplier = isMultimodal ? 1.5m : 1.0m;
            decimal totalCost = tokenCount * baseRate * multiplier;

            return new OmniResult<decimal> { Value = totalCost };
        }
    }
}
