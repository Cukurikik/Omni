using System;
using Omni.Domain.Monads;

namespace Omni.Business.KnowledgeHarvest
{
    public class GraphManager
    {
        public Result<bool, Exception> ConstructGraph(string data)
        {
            if (string.IsNullOrEmpty(data)) return Result<bool, Exception>.Err(new Exception("No data"));
            return Result<bool, Exception>.Ok(true);
        }
    }
}
