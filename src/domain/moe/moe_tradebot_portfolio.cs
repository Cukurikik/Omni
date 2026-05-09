// moe_tradebot_portfolio.cs — Domain
// Layer: Domain — LLM-TradeBot Portfolio Manager
// Inspired by: LLM-TradeBot (Optimize futures trading)

using System;

namespace Omni.Domain.MoE
{
    public class FuturesPortfolio
    {
        public Guid AccountId { get; private set; }
        public decimal AvailableMargin { get; private set; }
        public decimal UsedMargin { get; private set; }
        public decimal MaxDrawdownLimit { get; private set; }
        public decimal PeakEquity { get; private set; }

        public FuturesPortfolio(Guid accountId, decimal initialCapital, decimal maxDrawdownLimit)
        {
            AccountId = accountId;
            AvailableMargin = initialCapital;
            UsedMargin = 0m;
            MaxDrawdownLimit = maxDrawdownLimit;
            PeakEquity = initialCapital;
        }

        public decimal TotalEquity => AvailableMargin + UsedMargin;

        public void ExecuteTrade(decimal marginRequired)
        {
            if (marginRequired > AvailableMargin)
            {
                throw new InvalidOperationException("Insufficient margin for trade.");
            }

            // Check drawdown constraint (Domain Rule: Stop trading if max drawdown hit)
            decimal currentDrawdown = (PeakEquity - TotalEquity) / PeakEquity;
            if (currentDrawdown >= MaxDrawdownLimit)
            {
                throw new InvalidOperationException("Account frozen: Max drawdown limit reached.");
            }

            AvailableMargin -= marginRequired;
            UsedMargin += marginRequired;
        }

        public void SettleTrade(decimal marginReleased, decimal pnl)
        {
            UsedMargin -= marginReleased;
            AvailableMargin += (marginReleased + pnl);
            
            if (TotalEquity > PeakEquity)
            {
                PeakEquity = TotalEquity; // High-water mark updated
            }
        }
    }
}
