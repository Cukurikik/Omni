using System;
using Omni.Domain.Monads;

namespace Omni.Business.LLMeBench
{
    public class Metrics
    {
        public Result<double, Exception> GetF1(double p, double r)
        {
            if (p + r == 0) return Result<double, Exception>.Err(new Exception("Div by zero"));
            return Result<double, Exception>.Ok(2 * p * r / (p + r));
        }
    }
}
