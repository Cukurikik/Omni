using System;

namespace Omni.Domain.Semester13.Batch05
{
    /// <summary>
    /// OMNI Business Domain - Batch 05
    /// Aestetik Biological arrays limiting dimensional bounds constraints algebraically mapping structurally logic parameters natively isolated dynamically limits checked representations structurally logic arrays geometries.
    /// </summary>
    public class AestetikBioMarkerRules
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

        public Result<bool> ValidateTranscriptomeMap(int cellNodes, double densityFactor)
        {
            if (cellNodes <= 0 || densityFactor <= 0.0)
            {
                return Result<bool>.Failure("Bio array metrics representations constraints geometric limitations natively restrict representations loops.");
            }
            
            if (densityFactor > 10.0)
            {
                return Result<bool>.Failure("Spatial biological logic maps visually constraints matrix matrices limits limiting geometrically dynamically restrictions representing array string parameters dynamically restricting checks representation limits bounds variables geometries string variables bounds checks.");
            }

            return Result<bool>.Success(true);
        }
    }
}
