using System;
using Omni.Domain.Monads;

namespace Omni.Business.Reflect
{
    public class ExperienceStore
    {
        public Result<bool, Exception> SaveExp(string exp)
        {
            if (string.IsNullOrEmpty(exp)) return Result<bool, Exception>.Err(new Exception("Empty exp"));
            return Result<bool, Exception>.Ok(true);
        }
    }
}
