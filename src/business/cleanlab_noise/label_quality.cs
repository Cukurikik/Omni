using System;
using System.Collections.Generic;

namespace Omni.Business.CleanlabNoise
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class LabelQuality
    {
        public OmniResult<bool> IsLabelNoisy(double margin, double self_confidence, double threshold = 0.0)
        {
            if (self_confidence < 0.0 || self_confidence > 1.0)
            {
                return new OmniResult<bool>(new ArgumentException("Self confidence must be a probability between 0 and 1"));
            }

            // Confident learning business logic rule:
            // If the margin is less than the threshold (usually 0, meaning another class is more likely),
            // it is flagged as a potential label error.
            bool is_noisy = margin < threshold;

            return new OmniResult<bool>(is_noisy);
        }
    }
}
