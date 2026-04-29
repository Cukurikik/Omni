using System;
using Omni.Domain.Monads;

namespace Omni.Business.LangchainPrefect
{
    public class StateTracker
    {
        public Result<string, Exception> GetState(int id)
        {
            if (id <= 0) return Result<string, Exception>.Err(new Exception("Invalid ID"));
            return Result<string, Exception>.Ok("COMPLETED");
        }
    }
}
