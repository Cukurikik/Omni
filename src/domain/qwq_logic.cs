using System;
using Omni.Domain.Monads;

namespace Omni.Business.QwQ
{
    public class QwQLogic
    {
        public Result<bool, Exception> ValidateReasoning(string r)
        {
            if (string.IsNullOrEmpty(r)) return Result<bool, Exception>.Err(new Exception("Empty reasoning"));
            return Result<bool, Exception>.Ok(true);
        }
    }
}
