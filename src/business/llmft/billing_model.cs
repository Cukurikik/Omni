using System;

namespace Omni.LLMFT
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk => string.IsNullOrEmpty(Error);
    }

    public class BillingModel
    {
        public OmniResult<decimal> CalculateCost(int gpuHours, decimal ratePerHour)
        {
            if (gpuHours < 0 || ratePerHour < 0)
            {
                return new OmniResult<decimal> { Error = "Values cannot be negative" };
            }

            // Enterprise C# billing calculation for LLM fine-tuning
            decimal cost = gpuHours * ratePerHour;

            return new OmniResult<decimal> { Value = cost };
        }
    }
}
