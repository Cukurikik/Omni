// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// ML-Agents PPO Trainer (OMNI Zero-Mock Implementation)
// Implements Proximal Policy Optimization clipping loss in C#.

using System;
using System.Collections.Generic;

namespace Omni.Compute.MLAgents {

    public class Result<T> {
        public T Value;
        public string Error;
        public bool IsOk;

        public static Result<T> Ok(T val) => new Result<T> { Value = val, IsOk = true };
        public static Result<T> Err(string err) => new Result<T> { Error = err, IsOk = false };
    }

    public class PPOTrainer {
        private double clipEpsilon;

        public PPOTrainer(double epsilon = 0.2) {
            this.clipEpsilon = epsilon;
        }

        public Result<double> ComputeClippedSurrogateObjective(
            double advantage, double oldLogProb, double newLogProb) {
            
            if (double.IsNaN(advantage) || double.IsNaN(oldLogProb) || double.IsNaN(newLogProb)) {
                return Result<double>.Err("NaN values encountered in PPO step.");
            }

            // Ratio of policies r_t(theta) = exp(newLogProb - oldLogProb)
            double ratio = Math.Exp(newLogProb - oldLogProb);

            // Unclipped surrogate
            double unclipped = ratio * advantage;

            // Clipped surrogate
            double clippedRatio = Math.Clamp(ratio, 1.0 - clipEpsilon, 1.0 + clipEpsilon);
            double clipped = clippedRatio * advantage;

            // Return the pessimistic approximation (minimum)
            double loss = Math.Min(unclipped, clipped);

            // Note: Optimizers *minimize* loss, so we return negative of the objective
            return Result<double>.Ok(-loss); 
        }
    }
}
