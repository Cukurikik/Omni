using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.MultimodalSearch
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SearchResult
    {
        public string ItemId { get; set; }
        public double Score { get; set; }
    }

    public class RankingLogic
    {
        public OmniResult<List<SearchResult>> RankResults(List<SearchResult> rawResults, double minThreshold, int topK)
        {
            if (rawResults == null)
            {
                return new OmniResult<List<SearchResult>>(new ArgumentNullException(nameof(rawResults)));
            }

            if (minThreshold < 0 || minThreshold > 1)
            {
                return new OmniResult<List<SearchResult>>(new ArgumentException("Threshold must be between 0 and 1"));
            }

            if (topK <= 0)
            {
                return new OmniResult<List<SearchResult>>(new ArgumentException("topK must be > 0"));
            }

            // Business logic: Filter by threshold, sort by score descending, take top K
            var ranked = rawResults
                .Where(r => r.Score >= minThreshold)
                .OrderByDescending(r => r.Score)
                .Take(topK)
                .ToList();

            return new OmniResult<List<SearchResult>>(ranked);
        }
    }
}
