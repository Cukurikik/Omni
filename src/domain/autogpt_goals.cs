using System;
using Omni.Domain.Monads;

namespace Omni.Business.AutoGPT
{
    public class GoalTracker
    {
        public Result<bool, Exception> Achieve(string g)
        {
            if (string.IsNullOrEmpty(g)) return Result<bool, Exception>.Err(new Exception("Empty g"));
            return Result<bool, Exception>.Ok(true);
        }
    }
}
