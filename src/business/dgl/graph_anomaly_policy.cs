using System;

namespace Omni.DGL
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk { get; set; }
    }

    public class GraphAnomalyPolicy
    {
        public OmniResult<bool> IsAnomaly(double[] nodeEmbedding)
        {
            if (nodeEmbedding == null || nodeEmbedding.Length == 0)
            {
                return new OmniResult<bool> { Error = "Invalid embedding", IsOk = false };
            }
            
            // C# business rules for detecting fraud in DGL embeddings
            bool isAnomaly = nodeEmbedding[0] > 5.0; // threshold
            
            return new OmniResult<bool> { Value = isAnomaly, IsOk = true };
        }
    }
}
