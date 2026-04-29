// OMNI Domain Layer - Oumi Eval Metrics
namespace Omni.Domain.Oumi {
    public enum MetricError { None, OutOfBounds }

    public class Result<T> {
        public T Value { get; }
        public MetricError Error { get; }
        public bool IsOk => Error == MetricError.None;

        public Result(T value) { Value = value; Error = MetricError.None; }
        public Result(MetricError error) { Error = error; }
    }

    public class EvaluationValidator {
        public Result<bool> ValidatePassAtK(double score) {
            if (score < 0.0 || score > 1.0) {
                return new Result<bool>(MetricError.OutOfBounds);
            }
            return new Result<bool>(true);
        }
    }
}
