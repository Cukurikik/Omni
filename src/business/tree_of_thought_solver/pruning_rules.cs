using System;

namespace Omni.Business.TreeOfThoughtSolver
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class PruningRules
    {
        public OmniResult<bool> ShouldPruneBranch(double relevance_score, int depth)
        {
            if (relevance_score < 0.0 || relevance_score > 1.0 || depth < 0)
            {
                return new OmniResult<bool>(new ArgumentException("Invalid score or depth"));
            }

            // Tree of Thoughts Business Logic: Branch Pruning Heuristics
            // Halts exploration of reasoning paths that have low probability of success
            // saving massive amounts of API tokens
            
            if (depth > 5 && relevance_score < 0.4)
            {
                // Deep into a bad thought path, prune it
                return new OmniResult<bool>(true);
            }
            
            if (relevance_score < 0.1)
            {
                // Immediate nonsense generation, prune immediately
                return new OmniResult<bool>(true);
            }

            // Keep exploring
            return new OmniResult<bool>(false);
        }
    }
}
