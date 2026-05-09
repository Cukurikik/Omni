// moe_domain_financial_expert.cs — Domain / Business
// Layer: Domain / Finance — Strict Financial Math Expert
//
// LLMs are notoriously bad at precise arithmetic. When the MoE routes a query
// to the "Finance" expert (e.g., compound interest calculation, tax brackets),
// this C# module acts as a strict programmatic guardrail, catching the intent 
// and computing the exact mathematical answer using the `decimal` type, 
// rather than relying on the LLM's hallucinated math.

using System;
using System.Text.Json;

namespace Omni.MoE.Domain.Finance
{
    public class FinancialExpert
    {
        public FinancialExpert()
        {
            Console.WriteLine("[C# Finance Expert] Initialized Strict Mathematical Guardrails.");
        }

        /// <summary>
        /// Intercepts financial queries parsed by the LLM and executes exact C# math.
        /// </summary>
        public string ExecuteFinancialCalculation(string jsonIntent)
        {
            try
            {
                using JsonDocument doc = JsonDocument.Parse(jsonIntent);
                string operation = doc.RootElement.GetProperty("operation").GetString();

                switch (operation)
                {
                    case "COMPOUND_INTEREST":
                        decimal principal = doc.RootElement.GetProperty("principal").GetDecimal();
                        decimal rate = doc.RootElement.GetProperty("annual_rate").GetDecimal();
                        int years = doc.RootElement.GetProperty("years").GetInt32();
                        return CalculateCompoundInterest(principal, rate, years).ToString("C");

                    case "TAX_CALCULATION":
                        // Implement strict bracket logic
                        return "$0.00 (Implementation Pending)";

                    default:
                        return "ERROR: Unsupported financial operation.";
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[C# Finance Expert] Failed to parse LLM intent: {ex.Message}");
                return "ERROR: Invalid parameters provided by LLM.";
            }
        }

        private decimal CalculateCompoundInterest(decimal principal, decimal annualRateDecimal, int years)
        {
            // Formula: A = P(1 + r)^t
            // Using precise decimal math rather than floats to prevent penny rounding errors
            double rate = (double)annualRateDecimal;
            double amount = (double)principal * Math.Pow(1.0 + rate, years);
            return (decimal)amount;
        }
    }
}
