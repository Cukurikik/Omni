// OMNI Business Layer: graphrag_domain.cs
// C# Domain entities for GraphRAG document clusters.
// Bound: Max 50 documents per knowledge cluster.

using System;
using System.Collections.Generic;

namespace Omni.Semester14.Batch6.Business
{
    public class OmniError
    {
        public int Code { get; set; }
        public string Message { get; set; }
    }

    public class OmniResult<T>
    {
        public T Data { get; set; }
        public OmniError Error { get; set; }
    }

    public class KnowledgeCluster
    {
        private const int MAX_DOCS = 50;
        private List<string> _documentIds = new List<string>();

        public string ClusterId { get; set; }

        public OmniResult<bool> AddDocument(string docId)
        {
            if (_documentIds.Count >= MAX_DOCS)
            {
                return new OmniResult<bool> 
                { 
                    Data = false, 
                    Error = new OmniError { Code = 1, Message = "Knowledge cluster exceeds 50 document limit." } 
                };
            }

            _documentIds.Add(docId);
            return new OmniResult<bool> { Data = true, Error = null };
        }
    }
}
