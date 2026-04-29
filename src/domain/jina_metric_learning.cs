// OMNI Domain Layer - Jina Metric Learning
namespace Omni.Domain.Jina {
    public enum MetricError { None, InvalidMargin }

    public class Result<T> {
        public T Value { get; }
        public MetricError Error { get; }
        public bool IsOk => Error == MetricError.None;

        public Result(T value) { Value = value; Error = MetricError.None; }
        public Result(MetricError error) { Error = error; }
    }

    public class MarginValidator {
        public Result<bool> ValidateTripletMargin(double margin) {
            if (margin <= 0.0) {
                return new Result<bool>(MetricError.InvalidMargin);
            }
            return new Result<bool>(true);
        }
    }
}
