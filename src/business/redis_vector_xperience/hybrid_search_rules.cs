using System;

namespace Omni.Business.RedisVectorXperience
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class HybridSearchRules
    {
        public OmniResult<double> CalculateHybridScore(double vector_similarity, double bm25_score, double alpha)
        {
            if (alpha < 0.0 || alpha > 1.0)
            {
                return new OmniResult<double>(new ArgumentException("Alpha weight must be between 0.0 and 1.0"));
            }

            if (vector_similarity < 0.0 || bm25_score < 0.0)
            {
                 return new OmniResult<double>(new ArgumentException("Scores must be non-negative"));
            }

            // Redis Vector Xperience Business Logic: Reciprocal Rank Fusion or Convex Combination
            // Alpha = 1.0 means pure Vector Search, Alpha = 0.0 means pure Full-Text BM25 Search
            
            // Normalize BM25 score (heuristic approach assuming max BM25 ~ 50.0)
            double normalized_bm25 = Math.Min(1.0, bm25_score / 50.0);
            
            // Convex combination
            double hybrid_score = (alpha * vector_similarity) + ((1.0 - alpha) * normalized_bm25);

            return new OmniResult<double>(hybrid_score);
        }
    }
}
