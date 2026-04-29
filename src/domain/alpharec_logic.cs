using System;
using Omni.Domain.Monads;

namespace Omni.Business.AlphaRec
{
    public class RecommendationEngine
    {
        public Result<double, Exception> GetScore(double[] features)
        {
            if (features == null || features.Length == 0) return Result<double, Exception>.Err(new Exception("Invalid features"));
            return Result<double, Exception>.Ok(99.9);
        }
    }
}
