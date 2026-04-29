// OMNI Domain Layer - DS2 Curation
using System;
using System.Collections.Generic;

namespace Omni.Domain.DS2 {
    public enum CurationError { None, EmptyBatch, ScoreOutOfBounds }

    public class Result<T> {
        public T Value { get; }
        public CurationError Error { get; }
        public bool IsOk => Error == CurationError.None;

        public Result(T value) { Value = value; Error = CurationError.None; }
        public Result(CurationError error) { Error = error; }
    }

    public record RatingBatch(Guid Id, List<double> Scores);

    public class CurationPolicy {
        public Result<double> CalculateEffectiveScore(RatingBatch batch) {
            if (batch.Scores.Count == 0) return new Result<double>(CurationError.EmptyBatch);
            
            double sum = 0;
            foreach (var score in batch.Scores) {
                if (score < 0 || score > 1) return new Result<double>(CurationError.ScoreOutOfBounds);
                sum += score;
            }
            return new Result<double>(sum / batch.Scores.Count);
        }
    }
}
