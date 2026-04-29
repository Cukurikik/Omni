using System;
using Omni.Domain.Monads;

namespace Omni.Business.MemGPT
{
    public class ContextManager
    {
        public Result<int, Exception> Evict(int tokens)
        {
            if (tokens <= 0) return Result<int, Exception>.Err(new Exception("Invalid tokens"));
            return Result<int, Exception>.Ok(tokens);
        }
    }
}
