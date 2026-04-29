using System;

namespace Omni.Business.ToolOrchestra
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public string Error { get; }
        public bool IsOk { get; }

        public OmniResult(T value, string error = null)
        {
            Value = value;
            Error = error;
            IsOk = error == null;
        }
    }

    public class RLRewardCalculator
    {
        public OmniResult<double> CalculateReward(int toolCalls, bool taskSuccess)
        {
            if (toolCalls < 0)
            {
                return new OmniResult<double>(0, "Tool calls cannot be negative");
            }

            // Reward shaping: +10 for success, -0.1 per tool call to encourage efficiency
            double baseReward = taskSuccess ? 10.0 : -5.0;
            double penalty = toolCalls * 0.1;
            
            return new OmniResult<double>(baseReward - penalty);
        }
    }
}
