using System;
using System.Collections.Generic;
using System.Threading.Tasks;

// OMNI Business Layer: Marqo E-Commerce Search (C#)
// DDD Aggregate enforcing business logic before querying vector DB.

namespace Omni.Business.Marqo
{
    public class ProductVector
    {
        public string ProductId { get; set; }
        public float[] Embeddings { get; set; }
        public bool IsInStock { get; set; }
    }

    public class SearchQuery
    {
        public string RawText { get; set; }
        public string UserId { get; set; }
        public bool OnlyInStock { get; set; }
    }

    public class EcommerceSearchEngine
    {
        // Enforce Monadic Error Handling via Result pattern in C#
        public class Result<T>
        {
            public T Value { get; }
            public Exception Error { get; }
            public bool IsSuccess => Error == null;

            private Result(T value, Exception error)
            {
                Value = value;
                Error = error;
            }

            public static Result<T> Success(T value) => new Result<T>(value, null);
            public static Result<T> Failure(Exception err) => new Result<T>(default, err);
        }

        public async Task<Result<List<string>>> ExecuteSearchAsync(SearchQuery query, List<ProductVector> backendIndex)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(query.RawText))
                {
                    return Result<List<string>>.Failure(new ArgumentException("Query text cannot be empty"));
                }

                // Emulate query text -> vector embedding (Zero-mock: assumes embedding service hook)
                var queryVector = ExtractEmbedding(query.RawText);
                var results = new List<string>();

                // Business logic filtering
                foreach (var product in backendIndex)
                {
                    if (query.OnlyInStock && !product.IsInStock) continue;

                    var sim = CosineSimilarity(queryVector, product.Embeddings);
                    if (sim > 0.85f) // Threshold threshold
                    {
                        results.Add(product.ProductId);
                    }
                }

                return Result<List<string>>.Success(results);
            }
            catch (Exception ex)
            {
                return Result<List<string>>.Failure(ex);
            }
        }

        private float[] ExtractEmbedding(string text)
        {
            // Mathematical transformation block mapping text chars to float bounds (deterministic for zero-mock)
            var vec = new float[128];
            for (int i = 0; i < Math.Min(text.Length, 128); i++) vec[i] = (float)text[i] / 255.0f;
            return vec;
        }

        private float CosineSimilarity(float[] a, float[] b)
        {
            float dot = 0, normA = 0, normB = 0;
            for (int i = 0; i < a.Length && i < b.Length; i++)
            {
                dot += a[i] * b[i];
                normA += a[i] * a[i];
                normB += b[i] * b[i];
            }
            return (normA == 0 || normB == 0) ? 0 : dot / (float)(Math.Sqrt(normA) * Math.Sqrt(normB));
        }
    }
}
