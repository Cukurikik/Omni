using System;
using System.Collections.Generic;

// OMNI C# Business Layer: Seldon Deployment Strategy
// Domain-Driven Design logic for managing ML model rollout strategies.

namespace Omni.Business.Seldon
{
    public enum RolloutStatus { Pending, Active, Paused, Failed, Completed }
    public enum StrategyType { Canary, ABTesting, Shadow }

    public class SeldonDeployment
    {
        public Guid DeploymentId { get; private set; }
        public string ModelName { get; private set; }
        public StrategyType Strategy { get; private set; }
        public int TrafficPercentage { get; private set; }
        public RolloutStatus Status { get; private set; }

        private SeldonDeployment(string modelName, StrategyType strategy)
        {
            DeploymentId = Guid.NewGuid();
            ModelName = modelName;
            Strategy = strategy;
            TrafficPercentage = 0;
            Status = RolloutStatus.Pending;
        }

        public static Result<SeldonDeployment, string> Create(string modelName, StrategyType strategy)
        {
            if (string.IsNullOrWhiteSpace(modelName))
                return Result<SeldonDeployment, string>.Err("Model name cannot be empty.");

            return Result<SeldonDeployment, string>.Ok(new SeldonDeployment(modelName, strategy));
        }

        public Result<bool, string> AdjustTraffic(int percentage)
        {
            if (percentage < 0 || percentage > 100)
                return Result<bool, string>.Err("Traffic percentage must be between 0 and 100.");

            if (Status == RolloutStatus.Failed)
                return Result<bool, string>.Err("Cannot adjust traffic on a failed deployment.");

            TrafficPercentage = percentage;
            
            if (TrafficPercentage == 100)
                Status = RolloutStatus.Completed;
            else if (TrafficPercentage > 0)
                Status = RolloutStatus.Active;

            return Result<bool, string>.Ok(true);
        }

        public void FailDeployment()
        {
            Status = RolloutStatus.Failed;
            TrafficPercentage = 0; // Cut traffic immediately
        }
    }

    // Monadic Result Wrapper
    public struct Result<T, E>
    {
        public readonly T Value;
        public readonly E Error;
        public readonly bool IsOk;

        private Result(T value, E error, bool isOk)
        {
            Value = value;
            Error = error;
            IsOk = isOk;
        }

        public static Result<T, E> Ok(T value) => new Result<T, E>(value, default, true);
        public static Result<T, E> Err(E error) => new Result<T, E>(default, error, false);
    }
}
