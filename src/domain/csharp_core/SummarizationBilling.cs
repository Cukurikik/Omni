using System;

namespace Omni.Domain.Billing
{
    public class SummarizationBilling
    {
        public decimal RatePerToken { get; }

        public SummarizationBilling(decimal ratePerToken)
        {
            if (ratePerToken < 0) throw new ArgumentException("Rate cannot be negative");
            RatePerToken = ratePerToken;
        }

        public decimal CalculateCost(int tokenCount)
        {
            if (tokenCount < 0) throw new ArgumentException("Token count cannot be negative");
            return tokenCount * RatePerToken;
        }
    }
}
