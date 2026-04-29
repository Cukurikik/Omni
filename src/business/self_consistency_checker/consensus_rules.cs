using System;

namespace Omni.Business.SelfConsistencyChecker
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ConsensusRules
    {
        public OmniResult<bool> IsConsensusReached(int total_samples, int majority_votes)
        {
            if (total_samples <= 0 || majority_votes < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Invalid sample counts"));
            }

            // Self-Consistency Business Logic: Consensus Thresholds
            // Determines if the LLM is "sure" of its answer based on multiple temperature-sampled generations
            
            double ratio = (double)majority_votes / total_samples;
            
            // Require > 60% agreement for consensus
            if (ratio > 0.6)
            {
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(false);
        }
    }
}
