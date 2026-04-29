using System;
using System.Collections.Generic;

namespace Omni.Business.AgenticContext
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ContextRules
    {
        private readonly double _retentionThreshold;

        public ContextRules(double retentionThreshold = 0.5)
        {
            _retentionThreshold = retentionThreshold;
        }

        public OmniResult<bool> ShouldRetainExperience(double relevanceScore, double noveltyScore)
        {
            if (relevanceScore < 0 || relevanceScore > 1.0)
                return new OmniResult<bool>(new ArgumentException("Relevance score must be between 0 and 1"));

            if (noveltyScore < 0 || noveltyScore > 1.0)
                return new OmniResult<bool>(new ArgumentException("Novelty score must be between 0 and 1"));

            // Business logic: retain experience if it is highly relevant or sufficiently novel
            double retentionValue = (relevanceScore * 0.7) + (noveltyScore * 0.3);
            
            bool retain = retentionValue >= _retentionThreshold;

            return new OmniResult<bool>(retain);
        }
    }
}
