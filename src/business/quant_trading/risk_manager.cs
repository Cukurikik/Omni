using System;

namespace Omni.Business.QuantTrading
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class RiskManager
    {
        private readonly double _maxDrawdownLimit;
        private readonly double _maxPositionSize;

        public RiskManager(double maxDrawdownLimit = 0.10, double maxPositionSize = 100000)
        {
            _maxDrawdownLimit = maxDrawdownLimit;
            _maxPositionSize = maxPositionSize;
        }

        public OmniResult<string> EvaluateTrade(int signal, double accountBalance, double currentDrawdown)
        {
            if (accountBalance <= 0)
                return new OmniResult<string>(new InvalidOperationException("Account balance must be positive"));

            if (currentDrawdown >= _maxDrawdownLimit)
                return new OmniResult<string>(new InvalidOperationException($"Trading halted: Max drawdown {_maxDrawdownLimit} breached"));

            if (signal == 0)
                return new OmniResult<string>("HOLD");

            double proposedSize = accountBalance * 0.05; // 5% risk per trade
            if (proposedSize > _maxPositionSize)
            {
                proposedSize = _maxPositionSize;
            }

            string action = signal > 0 ? "BUY" : "SELL";
            return new OmniResult<string>($"APPROVED:{action}:{proposedSize:F2}");
        }
    }
}
