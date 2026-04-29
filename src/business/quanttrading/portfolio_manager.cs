using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.QuantTrading
{
    public class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T data) { Data = data; }
        public OmniResult(string error) { Error = error; }
    }

    public class AssetPosition
    {
        public string Symbol { get; set; }
        public decimal Quantity { get; set; }
        public decimal AveragePrice { get; set; }
    }

    public class PortfolioManager
    {
        private readonly Dictionary<string, AssetPosition> _portfolio = new Dictionary<string, AssetPosition>();
        private decimal _cashBalance;

        public PortfolioManager(decimal initialCash)
        {
            _cashBalance = initialCash;
        }

        public OmniResult<bool> ExecuteTradeRequest(string symbol, int actionType, decimal currentPrice)
        {
            if (string.IsNullOrEmpty(symbol) || currentPrice <= 0)
            {
                return new OmniResult<bool>("Invalid trade parameters.");
            }

            // Action: 0 = Hold, 1 = Buy, 2 = Sell
            if (actionType == 0)
            {
                return new OmniResult<bool>(true);
            }
            else if (actionType == 1) // Buy logic
            {
                decimal allocation = _cashBalance * 0.1m; // Risk 10% per trade
                if (allocation < currentPrice) return new OmniResult<bool>("Insufficient funds for 1 unit.");

                decimal qtyToBuy = allocation / currentPrice;
                _cashBalance -= allocation;

                if (!_portfolio.ContainsKey(symbol))
                {
                    _portfolio[symbol] = new AssetPosition { Symbol = symbol, Quantity = 0, AveragePrice = 0 };
                }

                var pos = _portfolio[symbol];
                pos.AveragePrice = ((pos.Quantity * pos.AveragePrice) + allocation) / (pos.Quantity + qtyToBuy);
                pos.Quantity += qtyToBuy;

                return new OmniResult<bool>(true);
            }
            else if (actionType == 2) // Sell logic
            {
                if (!_portfolio.ContainsKey(symbol) || _portfolio[symbol].Quantity <= 0)
                {
                    return new OmniResult<bool>("No active position to sell.");
                }

                var pos = _portfolio[symbol];
                decimal proceeds = pos.Quantity * currentPrice;
                _cashBalance += proceeds;
                pos.Quantity = 0;
                
                return new OmniResult<bool>(true);
            }

            return new OmniResult<bool>($"Unknown action type: {actionType}");
        }

        public decimal GetTotalValue(Dictionary<string, decimal> currentPrices)
        {
            decimal total = _cashBalance;
            foreach (var pos in _portfolio.Values)
            {
                if (currentPrices.TryGetValue(pos.Symbol, out decimal price))
                {
                    total += pos.Quantity * price;
                }
            }
            return total;
        }
    }
}
