using System;

namespace Omni.Business.RL
{
    // OMNI RL - Adaptive Discount Factor Calculator
    // Strict error handling and mathematical precision for RL gamma adjustments

    public struct GammaResult
    {
        public double Value { get; }
        public Exception Error { get; }
        public bool IsSuccess => Error == null;

        public GammaResult(double value)
        {
            Value = value;
            Error = null;
        }

        public GammaResult(Exception error)
        {
            Value = 0;
            Error = error;
        }
    }

    public class AdaptiveDiscountFactor
    {
        private readonly double _initialGamma;
        private readonly double _targetGamma;
        private readonly int _totalSteps;

        public AdaptiveDiscountFactor(double initialGamma = 0.90, double targetGamma = 0.999, int totalSteps = 1000000)
        {
            if (initialGamma < 0 || initialGamma > 1 || targetGamma < 0 || targetGamma > 1)
            {
                throw new ArgumentException("Gamma must be between 0 and 1.");
            }
            if (totalSteps <= 0)
            {
                throw new ArgumentException("Total steps must be positive.");
            }

            _initialGamma = initialGamma;
            _targetGamma = targetGamma;
            _totalSteps = totalSteps;
        }

        public GammaResult Calculate(int currentStep)
        {
            try
            {
                if (currentStep < 0)
                {
                    return new GammaResult(new ArgumentException("Current step cannot be negative."));
                }

                if (currentStep >= _totalSteps)
                {
                    return new GammaResult(_targetGamma);
                }

                // Linear interpolation
                double progress = (double)currentStep / _totalSteps;
                double currentGamma = _initialGamma + progress * (_targetGamma - _initialGamma);

                return new GammaResult(currentGamma);
            }
            catch (Exception ex)
            {
                return new GammaResult(ex);
            }
        }
    }
}
