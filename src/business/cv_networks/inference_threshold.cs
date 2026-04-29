using System;
using System.Collections.Generic;

namespace Omni.Business.CVNetworks
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class InferenceThreshold
    {
        private readonly double _confidenceThreshold;

        public InferenceThreshold(double confidenceThreshold = 0.85)
        {
            _confidenceThreshold = confidenceThreshold;
        }

        public OmniResult<List<string>> FilterPredictions(Dictionary<string, double> rawPredictions)
        {
            if (rawPredictions == null)
                return new OmniResult<List<string>>(new ArgumentNullException(nameof(rawPredictions)));

            var acceptedClasses = new List<string>();

            // Business logic: only accept classes strictly above mathematical threshold
            foreach (var kvp in rawPredictions)
            {
                if (kvp.Value >= _confidenceThreshold)
                {
                    acceptedClasses.Add(kvp.Key);
                }
            }

            // Deterministic sort for consistent output ordering
            acceptedClasses.Sort();

            return new OmniResult<List<string>>(acceptedClasses);
        }
    }
}
