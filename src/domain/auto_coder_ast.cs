using System;
using Omni.Domain.Monads;

namespace Omni.Business.AutoCoder
{
    public class ASTParser
    {
        public Result<bool, Exception> Parse(string code)
        {
            if (string.IsNullOrEmpty(code)) return Result<bool, Exception>.Err(new Exception("No code"));
            return Result<bool, Exception>.Ok(true);
        }
    }
}
