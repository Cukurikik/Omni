using System;
using Omni.Domain.Monads;

namespace Omni.Business.MetaGPT
{
    public class PRD
    {
        public Result<bool, Exception> Validate(string prd)
        {
            if (string.IsNullOrEmpty(prd)) return Result<bool, Exception>.Err(new Exception("No PRD"));
            return Result<bool, Exception>.Ok(true);
        }
    }
}
