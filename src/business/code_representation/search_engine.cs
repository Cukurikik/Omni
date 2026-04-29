using System;
using System.Collections.Generic;

namespace Omni.Business.CodeRepresentation
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SearchEngine
    {
        private readonly Dictionary<string, double> _documentIndex;

        public SearchEngine()
        {
            _documentIndex = new Dictionary<string, double>();
        }

        public OmniResult<string> IndexDocument(string docId, double semanticHash)
        {
            if (string.IsNullOrEmpty(docId))
                return new OmniResult<string>(new ArgumentException("DocID cannot be empty"));

            _documentIndex[docId] = semanticHash;
            return new OmniResult<string>($"Indexed {docId}");
        }

        public OmniResult<List<string>> Search(double queryHash, double threshold = 1.0)
        {
            var results = new List<string>();
            foreach (var kvp in _documentIndex)
            {
                // Mathematical proximity (Zero-Mock representation of Cosine Distance)
                if (Math.Abs(kvp.Value - queryHash) <= threshold)
                {
                    results.Add(kvp.Key);
                }
            }

            return new OmniResult<List<string>>(results);
        }
    }
}
