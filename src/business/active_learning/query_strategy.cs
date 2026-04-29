using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.ActiveLearning
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class DataSample
    {
        public string Id { get; set; }
        public double UncertaintyScore { get; set; }
    }

    public class QueryStrategy
    {
        private readonly double _entropyThreshold;

        public QueryStrategy(double entropyThreshold = 0.8)
        {
            _entropyThreshold = entropyThreshold;
        }

        public OmniResult<List<DataSample>> SelectSamplesForLabeling(List<DataSample> pool, int k)
        {
            if (pool == null || pool.Count == 0)
                return new OmniResult<List<DataSample>>(new ArgumentException("Pool cannot be empty"));

            if (k <= 0)
                return new OmniResult<List<DataSample>>(new ArgumentException("k must be greater than 0"));

            // Strategy: Select top K uncertain samples that are above the threshold
            var selected = pool
                .Where(s => s.UncertaintyScore >= _entropyThreshold)
                .OrderByDescending(s => s.UncertaintyScore)
                .Take(k)
                .ToList();

            return new OmniResult<List<DataSample>>(selected);
        }
    }
}
