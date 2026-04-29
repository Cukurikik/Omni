// OMNI Domain Layer - RAGAS Metrics
namespace Omni.Domain.RAGAS {
    public enum MetricError { None, OutOfBounds }

    public class Result<T> {
        public T Value { get; }
        public MetricError Error { get; }
        public bool IsOk => Error == MetricError.None;

        public Result(T value) { Value = value; Error = MetricError.None; }
        public Result(MetricError error) { Error = error; }
    }

    public class ThresholdPolicy {
        public Result<bool> IsProductionReady(double score, double threshold) {
            if (score < 0 || score > 1) {
                return new Result<bool>(MetricError.OutOfBounds);
            }
            return new Result<bool>(score >= threshold);
        }
    }
}
