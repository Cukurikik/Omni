// OMNI Business — Inference Billing
using System;
using System.Threading.Tasks;

namespace OmniFramework.Business
{
    public class OmniInferenceBilling
    {
        private const decimal CostPer1KTokens = 0.002m;

        public async Task<Invoice> ChargeForInferenceAsync(string apiKey, int promptTokens, int completionTokens)
        {
            if (string.IsNullOrEmpty(apiKey))
                throw new ArgumentException("Invalid API Key");

            int totalTokens = promptTokens + completionTokens;
            decimal totalCost = (totalTokens / 1000m) * CostPer1KTokens;

            // Simulate DB Transaction
            await Task.Delay(50); 
            
            return new Invoice 
            {
                TransactionId = Guid.NewGuid(),
                TotalTokens = totalTokens,
                CostUsd = totalCost,
                Timestamp = DateTime.UtcNow
            };
        }
    }

    public class Invoice 
    {
        public Guid TransactionId { get; set; }
        public int TotalTokens { get; set; }
        public decimal CostUsd { get; set; }
        public DateTime Timestamp { get; set; }
    }
}
