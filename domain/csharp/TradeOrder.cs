using System;

// ==========================================
// 🏢 OMNI C# ENTERPRISE DOMAIN (Phase 49)
// ==========================================
// Menerapkan Domain-Driven Design (DDD) untuk
// menampung logika bisnis keras dan validasi Ledger.

namespace Omni.Domain.HighFrequencyTrading
{
    public class TradeOrder
    {
        public Guid Id { get; private set; }
        public string Symbol { get; private set; }
        public decimal BuyPrice { get; private set; }
        public decimal SellPrice { get; private set; }
        
        public OrderStatus Status { get; private set; }

        public TradeOrder(string symbol, decimal buyPrice, decimal sellPrice)
        {
            if (string.IsNullOrWhiteSpace(symbol))
                throw new ArgumentException("Simbol mata uang tidak boleh kosong.");
                
            if (sellPrice <= buyPrice)
                throw new InvalidOperationException("E002: Sinyal Invalid! Jual harus lebih tinggi dari Beli.");

            Id = Guid.NewGuid();
            Symbol = symbol;
            BuyPrice = buyPrice;
            SellPrice = sellPrice;
            Status = OrderStatus.PENDING;
        }

        public decimal CalculateSpread()
        {
            return SellPrice - BuyPrice;
        }

        public void MarkAsExecuted()
        {
            Status = OrderStatus.EXECUTED;
        }
    }

    public enum OrderStatus
    {
        PENDING,
        EXECUTED,
        FAILED
    }
}
