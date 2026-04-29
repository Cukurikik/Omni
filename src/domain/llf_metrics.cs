// OMNI Domain Layer - LLF Metrics
using System;

namespace Omni.Domain.LLFBench {
    public enum MetricError { None, InvalidScore }

    public class Result<T> {
        public T Value { get; }
        public MetricError Error { get; }
        public bool IsOk => Error == MetricError.None;

        public Result(T value) { Value = value; Error = MetricError.None; }
        public Result(MetricError error) { Error = error; }
    }

    public class MetricValidator {
        public Result<bool> ValidateScore(double score) {
            if (score < 0 || score > 1.0) {
                return new Result<bool>(MetricError.InvalidScore);
            }
            return new Result<bool>(true);
        }
    }
}
