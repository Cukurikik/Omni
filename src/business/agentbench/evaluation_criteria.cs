using System;

namespace Omni.AgentBench
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk { get; set; }
    }

    public class EvaluationCriteria
    {
        public OmniResult<bool> MeetsMinimumStandard(double score)
        {
            if (score < 0 || score > 100)
            {
                return new OmniResult<bool> { Error = "Invalid score range", IsOk = false };
            }
            
            // C# business rules determining if an agent meets the deployment threshold
            bool passes = score >= 75.0;
            
            return new OmniResult<bool> { Value = passes, IsOk = true };
        }
    }
}
