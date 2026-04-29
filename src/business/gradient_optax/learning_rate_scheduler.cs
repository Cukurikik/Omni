using System;

namespace Omni.Business.GradientOptax
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class LearningRateScheduler
    {
        private readonly double _initialLr;
        private readonly double _minLr;

        public LearningRateScheduler(double initialLr = 0.1, double minLr = 1e-6)
        {
            _initialLr = initialLr;
            _minLr = minLr;
        }

        public OmniResult<double> StepReduceLROnPlateau(double currentLoss, double bestLoss, double currentLr)
        {
            if (currentLoss < 0 || bestLoss < 0)
                return new OmniResult<double>(new ArgumentException("Loss cannot be negative"));

            if (currentLr < 0)
                return new OmniResult<double>(new ArgumentException("Learning rate cannot be negative"));

            // If loss didn't improve by at least 1%, reduce LR by half
            if (currentLoss > bestLoss * 0.99)
            {
                double nextLr = Math.Max(currentLr * 0.5, _minLr);
                return new OmniResult<double>(nextLr);
            }

            // Maintain current LR
            return new OmniResult<double>(currentLr);
        }
    }
}
