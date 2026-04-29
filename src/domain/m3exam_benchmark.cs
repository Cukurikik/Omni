using System;
using Omni.Domain.Monads;

namespace Omni.Business.M3Exam
{
    public class BenchmarkResult
    {
        public Result<string, Exception> Verify(double score)
        {
            if (score < 0 || score > 100) return Result<string, Exception>.Err(new Exception("Invalid score"));
            return Result<string, Exception>.Ok("PASSED");
        }
    }
}
