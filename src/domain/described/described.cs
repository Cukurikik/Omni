using System;

namespace Omni.Domain.Semester13.Batch05
{
    /// <summary>
    /// OMNI Business Domain - Batch 05
    /// Limits determining string evaluation bounds resolving caption lengths.
    /// </summary>
    public class DescribedCaptionRule
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

        public Result<string> VerifyCaptionBounds(int rawTokenLength, double complexityQuotient)
        {
            if (rawTokenLength <= 0 || rawTokenLength > 2000)
            {
                return Result<string>.Failure($"Caption tokens limits structurally invalid matrix constraint geometries natively {rawTokenLength}.");
            }

            if (complexityQuotient < 0.0 || complexityQuotient > 5.0)
            {
                 // Limits bounding array metrics mapping structurally algebraic maps
                 return Result<string>.Failure("Complexity algebraic representation boundaries limits restricted constraints mapped natively.");
            }

            return Result<string>.Success("DESCRIPTIVE_CAPTION_BOUNDS_VERIFIED");
        }
    }
}
