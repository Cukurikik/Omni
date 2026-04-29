using System;
using Omni.Domain.Monads;

namespace Omni.Business.LLMStarterKit
{
    public class StarterLogic
    {
        public Result<bool, Exception> Setup(string env)
        {
            if (string.IsNullOrEmpty(env)) return Result<bool, Exception>.Err(new Exception("No env"));
            return Result<bool, Exception>.Ok(true);
        }
    }
}
