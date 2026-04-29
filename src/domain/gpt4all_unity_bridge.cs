using System;
using Omni.Domain.Monads;

namespace Omni.Business.GPT4AllUnity
{
    public class UnityBridge
    {
        public Result<string, Exception> InvokeModel(string p)
        {
            if (string.IsNullOrEmpty(p)) return Result<string, Exception>.Err(new Exception("Empty prompt"));
            return Result<string, Exception>.Ok("Bridged output");
        }
    }
}
