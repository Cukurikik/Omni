// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// PapersWithCode (PWC) Indexer Engine (OMNI Zero-Mock Implementation)
// Implements exact Jaccard Similarity index for paper code overlap analysis.

using System;
using System.Collections.Generic;

namespace Omni.Compute.Pwc
{
    public class Result<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk { get; set; }

        public static Result<T> Ok(T val) => new Result<T> { Value = val, Error = null, IsOk = true };
        public static Result<T> Err(string err) => new Result<T> { Value = default(T), Error = err, IsOk = false };
    }

    public class PaperIndexer
    {
        public Result<double> CalculateJaccardOverlap(HashSet<string> repoA_tokens, HashSet<string> repoB_tokens)
        {
            if (repoA_tokens == null || repoB_tokens == null)
            {
                 return Result<double>.Err("Token sets cannot be null.");
            }

            if (repoA_tokens.Count == 0 && repoB_tokens.Count == 0)
            {
                 return Result<double>.Ok(1.0); // Both empty, technically identical.
            }

            var intersectionCount = 0;
            foreach (var token in repoA_tokens)
            {
                if (repoB_tokens.Contains(token))
                {
                    intersectionCount++;
                }
            }

            var unionCount = repoA_tokens.Count + repoB_tokens.Count - intersectionCount;

            if (unionCount == 0) return Result<double>.Err("Zero division in union space.");

            double jaccard = (double)intersectionCount / unionCount;
            return Result<double>.Ok(jaccard);
        }
    }
}
