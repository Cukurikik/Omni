using System;
using Omni.Domain.Monads;

namespace Omni.Business.MistralHaystack
{
    public class PipelineManager
    {
        public Result<int, Exception> CountNodes(string pipeId)
        {
            if (string.IsNullOrEmpty(pipeId)) return Result<int, Exception>.Err(new Exception("Invalid ID"));
            return Result<int, Exception>.Ok(5);
        }
    }
}
