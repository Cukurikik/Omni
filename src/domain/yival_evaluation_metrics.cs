// OMNI Domain Layer - YiVal Evaluation Metrics
namespace Omni.Domain.YiVal {
    public enum EvalError { None, ScoreOutOfBounds }

    public class Result<T> {
        public T Value { get; }
        public EvalError Error { get; }
        public bool IsOk => Error == EvalError.None;

        public Result(T value) { Value = value; Error = EvalError.None; }
        public Result(EvalError error) { Error = error; }
    }

    public class MetricValidator {
        public Result<bool> ValidateEloRating(double elo) {
            if (elo < 0) {
                return new Result<bool>(EvalError.ScoreOutOfBounds);
            }
            return new Result<bool>(true);
        }
    }
}
