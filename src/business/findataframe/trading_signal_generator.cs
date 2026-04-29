using System;
using Omni.Core.Result;

namespace Omni.Business.FinDataFrame
{
    // OMNI BUSINESS LAYER: Trading Signal Generator
    // Generates strictly typed trading signals from indicator intersections.

    public enum SignalAction { Buy, Sell, Hold }

    public class TradingSignal
    {
        public string AssetId { get; set; }
        public SignalAction Action { get; set; }
        public double Confidence { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class TradingSignalGenerator
    {
        public OmniResult<TradingSignal, string> EvaluateCrossover(
            string assetId, double shortEma, double longEma, double previousShortEma, double previousLongEma)
        {
            try
            {
                SignalAction action = SignalAction.Hold;
                double confidence = 0.0;

                // Golden Cross
                if (previousShortEma <= previousLongEma && shortEma > longEma)
                {
                    action = SignalAction.Buy;
                    confidence = (shortEma - longEma) / longEma;
                }
                // Death Cross
                else if (previousShortEma >= previousLongEma && shortEma < longEma)
                {
                    action = SignalAction.Sell;
                    confidence = (longEma - shortEma) / longEma;
                }

                return OmniResult<TradingSignal, string>.Ok(new TradingSignal
                {
                    AssetId = assetId,
                    Action = action,
                    Confidence = Math.Min(confidence * 100, 1.0),
                    Timestamp = DateTime.UtcNow
                });
            }
            catch (Exception ex)
            {
                return OmniResult<TradingSignal, string>.Err($"Signal evaluation failed: {ex.Message}");
            }
        }
    }
}
