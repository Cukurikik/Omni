using System;

namespace Omni.Business.Finance {
    public class BacktestAggregate {
        public Guid BacktestId { get; private set; }
        public decimal TotalReturn { get; private set; }
        public decimal MaxDrawdown { get; private set; }

        public BacktestAggregate(Guid id, decimal totalReturn, decimal maxDrawdown) {
            BacktestId = id;
            TotalReturn = totalReturn;
            MaxDrawdown = maxDrawdown;
        }

        public bool IsProfitable() {
            return TotalReturn > 0;
        }
    }
}
