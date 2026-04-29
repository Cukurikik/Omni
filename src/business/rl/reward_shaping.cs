using System;
using System.Collections.Generic;

namespace Omni.Business.RL
{
    // OMNI RL - Reward Shaping Engine
    // Monadic error handling: Returns Result<T, Error> instead of throwing exceptions

    public struct Result<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsSuccess => Error == null;

        public Result(T value)
        {
            Value = value;
            Error = null;
        }

        public Result(Exception error)
        {
            Value = default;
            Error = error;
        }
    }

    public class RewardShaper
    {
        private readonly double _timePenalty;
        private readonly double _goalBonus;
        private readonly double _energyCost;

        public RewardShaper(double timePenalty = -0.01, double goalBonus = 100.0, double energyCost = -0.005)
        {
            _timePenalty = timePenalty;
            _goalBonus = goalBonus;
            _energyCost = energyCost;
        }

        public Result<double> ShapeReward(double baseReward, bool isGoalReached, double energyExpended)
        {
            try
            {
                if (energyExpended < 0)
                {
                    return new Result<double>(new ArgumentException("Energy expended cannot be negative."));
                }

                double shapedReward = baseReward + _timePenalty;
                
                if (isGoalReached)
                {
                    shapedReward += _goalBonus;
                }

                shapedReward += (energyExpended * _energyCost);

                return new Result<double>(shapedReward);
            }
            catch (Exception ex)
            {
                return new Result<double>(ex);
            }
        }

        public Result<double[]> ShapeBatch(double[] baseRewards, bool[] isGoalReached, double[] energyExpended)
        {
            if (baseRewards.Length != isGoalReached.Length || baseRewards.Length != energyExpended.Length)
            {
                return new Result<double[]>(new ArgumentException("Array lengths must match."));
            }

            double[] shapedRewards = new double[baseRewards.Length];
            for (int i = 0; i < baseRewards.Length; i++)
            {
                var result = ShapeReward(baseRewards[i], isGoalReached[i], energyExpended[i]);
                if (!result.IsSuccess)
                {
                    return new Result<double[]>(result.Error);
                }
                shapedRewards[i] = result.Value;
            }

            return new Result<double[]>(shapedRewards);
        }
    }
}
