using System;

namespace Omni.Domain.Semester13.Batch05
{
    /// <summary>
    /// OMNI Business Domain - Batch 05
    /// MELD sentiment policies extracting boundaries logically.
    /// </summary>
    public class MeldEthicsValidator
    {
        public class Result<T>
        {
            public T Value { get; }
            public string ErrorMessage { get; }
            public bool IsSuccess => ErrorMessage == null;
            
            private Result(T value, string error)
            {
                Value = value;
                ErrorMessage = error;
            }

            public static Result<T> Success(T val) => new Result<T>(val, null);
            public static Result<T> Failure(string err) => new Result<T>(default, err);
        }

        public Result<double> ParsePolicyVector(double emotionValence, bool hasExplicitAudio)
        {
            if (emotionValence < -1.0 || emotionValence > 1.0)
            {
                return Result<double>.Failure("Valence representation mappings mathematically restricted outside bounds [-1.0, 1.0].");
            }

            if (emotionValence < -0.8 && hasExplicitAudio)
            {
                return Result<double>.Failure("Policy constraints mapped logically preventing extreme negative audio metrics.");
            }

            return Result<double>.Success(emotionValence);
        }
    }
}
