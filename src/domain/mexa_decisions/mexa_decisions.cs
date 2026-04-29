using System;

namespace Omni.Semester13.Batch07.MexaDecisions
{
    public class MexaDecisionError : Exception
    {
        public MexaDecisionError(string msg) : base(msg) {}
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
    /// OMNI Engine: mexa-decisions
    /// Business routing logic for Mixture of Experts (MoE) execution confidence limits.
    /// </summary>
    public class MexaDecisionEngine
    {
        private readonly double _confidenceRejectionThreshold;

        public MexaDecisionEngine(double rejectionThreshold = 0.4)
        {
            _confidenceRejectionThreshold = rejectionThreshold;
        }

        public Result<bool> RouteToHumanFallback(double entropyConfidence, int activeExperts)
        {
            try
            {
                if (entropyConfidence < 0.0 || entropyConfidence > 1.0)
                    return new Result<bool>(new MexaDecisionError("Confidence boundary violation"));

                if (activeExperts <= 0)
                    return new Result<bool>(new MexaDecisionError("Zero active experts mathematically implausible"));

                // Fallback required if confidence is too low or not enough experts agreed
                bool needsFallback = entropyConfidence < _confidenceRejectionThreshold || activeExperts < 2;

                return new Result<bool>(needsFallback);
            }
            catch (Exception ex)
            {
                return new Result<bool>(new MexaDecisionError($"Routing computation failed: {ex.Message}"));
            }
        }

        public Result<double> CalculateConsensusPayout(double consensusScore)
        {
             try
             {
                  if (consensusScore < 0.0) return new Result<double>(new MexaDecisionError("Consensus mathematically cannot be negative in this domain."));
                  
                  double payout = consensusScore * 100.0;
                  
                  return new Result<double>(payout > 1000.0 ? 1000.0 : payout);
             }
             catch(Exception ex)
             {
                  return new Result<double>(new MexaDecisionError($"Payout computation map failed: {ex.Message}"));
             }
        }
    }
}
