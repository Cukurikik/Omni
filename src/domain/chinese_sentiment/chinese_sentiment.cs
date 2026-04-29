using System;

// OMNI CHINESE SENTIMENT DOMAIN RULES
// CQRS Domain Rule Engine regulating multi-class emotional constraints.

namespace Omni.Domain.ChineseSentiment
{
    public enum CQRSCommandStatus
    {
        Ok,
        ValidationFailed,
        SentimentThresholdBreached
    }

    public struct CommandResult<T>
    {
        public T Value;
        public string Error;
        public CQRSCommandStatus Status;
    }

    public class SentimentEmotionalLimits
    {
        public double PositivityLimit { get; private set; }
        public double NegativityLimit { get; private set; }

        public SentimentEmotionalLimits(double posLimit, double negLimit)
        {
            PositivityLimit = posLimit;
            NegativityLimit = negLimit;
        }

        public CommandResult<bool> ValidateExtractedSentiment(double positiveConfidence, double negativeConfidence)
        {
            if (positiveConfidence < 0.0 || positiveConfidence > 1.0 || 
                negativeConfidence < 0.0 || negativeConfidence > 1.0)
            {
                return new CommandResult<bool> 
                { 
                    Value = false, 
                    Error = "CONFIDENCE_OUT_OF_BOUNDS", 
                    Status = CQRSCommandStatus.ValidationFailed 
                };
            }

            // Zero-mock algorithmic bounds
            double combinedVariance = positiveConfidence * negativeConfidence;
            
            if (combinedVariance > 0.4)
            {
                return new CommandResult<bool>
                {
                    Value = false,
                    Error = "AMBIGUOUS_SENTIMENT_VARIANCE",
                    Status = CQRSCommandStatus.ValidationFailed
                };
            }

            if (negativeConfidence > NegativityLimit)
            {
                return new CommandResult<bool>
                {
                    Value = false,
                    Error = "EXTREME_NEGATIVITY_BOUNDARY_BREACH",
                    Status = CQRSCommandStatus.SentimentThresholdBreached
                };
            }

            return new CommandResult<bool>
            {
                Value = true,
                Error = string.Empty,
                Status = CQRSCommandStatus.Ok
            };
        }
    }
}
