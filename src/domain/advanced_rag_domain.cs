using System;
using Omni.Domain.Monads;

namespace Omni.Business.AdvancedRAG
{
    public class RAGManager
    {
        public Result<int, Exception> ProcessRAG(string query)
        {
            if (string.IsNullOrEmpty(query)) return Result<int, Exception>.Err(new Exception("query empty"));
            return Result<int, Exception>.Ok(2);
        }
    }
}
