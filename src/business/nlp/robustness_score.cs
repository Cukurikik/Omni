using System;

namespace Omni.Business.NLP
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }
        private Result(bool isSuccess, T value, E error) { IsSuccess = isSuccess; Value = value; Error = error; }
        public static Result<T, E> Success(T value) => new Result<T, E>(true, value, default!);
        public static Result<T, E> Failure(E error) => new Result<T, E>(false, default!, error);
    }

    public class RobustnessScorePayload 
    {
        public int OriginalLength { get; set; }
        public int EditDistance { get; set; }
        public bool AttackSucceeded { get; set; }
        public double ConfidenceDrop { get; set; }
    }

    public class RobustnessCalculator
    {
        public Result<double, string> CalculateScore(RobustnessScorePayload payload)
        {
            if (payload.OriginalLength <= 0) 
                return Result<double, string>.Failure("Original length must be > 0");
                
            if (payload.ConfidenceDrop < 0.0 || payload.ConfidenceDrop > 1.0)
                return Result<double, string>.Failure("Confidence drop must be between 0.0 and 1.0");

            double lengthRatio = (double)payload.EditDistance / payload.OriginalLength;
            // Cap length ratio to 1.0
            lengthRatio = Math.Min(lengthRatio, 1.0);
            
            // Formula: Higher edit distance needed to fool model = higher robustness
            // If attack failed, robustness gets a boost.
            
            double baseRobustness = lengthRatio * (1.0 - payload.ConfidenceDrop);
            
            if (!payload.AttackSucceeded)
            {
                baseRobustness += 0.5; // Bonus for deflecting the attack
            }
            
            // Normalize to 0-1
            double finalScore = Math.Max(0.0, Math.Min(1.0, baseRobustness));
            
            return Result<double, string>.Success(Math.Round(finalScore, 4));
        }
    }
}
