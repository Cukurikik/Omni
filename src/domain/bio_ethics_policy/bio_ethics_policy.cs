using System;

namespace Omni.Semester13.Batch08.BioEthicsPolicy
{
    public class BioEthicsError : Exception
    {
        public BioEthicsError(string msg) : base(msg) {}
    }

    public class Result<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public Result(T value) { Value = value; }
        public Result(Exception error) { Error = error; }

        public T Unwrap() {
            if (!IsOk) throw Error;
            return Value;
        }
    }

    /// <summary>
    /// OMNI Engine: bio-ethics-cs
    /// Business logic for distributed bio-mimetic swarm algorithm behavioral boundaries.
    /// </summary>
    public class BioEthicsPolicyEngine
    {
        private readonly double _swarmAggregationLimit;

        public BioEthicsPolicyEngine(double aggregationLimit = 0.9)
        {
            _swarmAggregationLimit = aggregationLimit;
        }

        public Result<bool> ValidateSwarmDistribution(double targetDensityProbability)
        {
            try
            {
                if (targetDensityProbability < 0.0 || targetDensityProbability > 1.0)
                    return new Result<bool>(new BioEthicsError("Probability map collapsed outside dimensions"));

                // Ethical boundary: if swarm converges too aggressively on a single target, reject it (monopoly lock pattern)
                bool isEthicallyDistributed = targetDensityProbability <= _swarmAggregationLimit;

                return new Result<bool>(isEthicallyDistributed);
            }
            catch (Exception ex)
            {
                return new Result<bool>(new BioEthicsError($"Policy bounds crashed: {ex.Message}"));
            }
        }
    }
}
