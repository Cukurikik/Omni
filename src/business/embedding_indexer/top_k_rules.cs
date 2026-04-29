using System;

namespace Omni.Business.EmbeddingIndexer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class RetrievalRules
    {
        public OmniResult<bool> ValidateTopKRequest(int top_k, double similarity_threshold)
        {
            if (top_k <= 0 || top_k > 1000)
            {
                return new OmniResult<bool>(new ArgumentException("Top-K must be between 1 and 1000 for system stability"));
            }

            if (similarity_threshold < -1.0 || similarity_threshold > 1.0)
            {
                return new OmniResult<bool>(new ArgumentException("Cosine similarity threshold must be bounded between -1.0 and 1.0"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
