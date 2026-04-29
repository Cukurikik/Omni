// OMNI Domain Layer - RWKU Metrics
namespace Omni.Domain.RWKU {
    public enum BenchError { None, InvalidForgettingScore }

    public class Result<T> {
        public T Value { get; }
        public BenchError Error { get; }
        public bool IsOk => Error == BenchError.None;

        public Result(T value) { Value = value; Error = BenchError.None; }
        public Result(BenchError error) { Error = error; }
    }

    public class ForgettingValidator {
        public Result<bool> ValidatePrivacyRetention(double forgettingScore, double utilityPreservation) {
            if (forgettingScore < 0 || forgettingScore > 1) {
                return new Result<bool>(BenchError.InvalidForgettingScore);
            }
            
            // RWKU requires high forgetting but stable utility
            return new Result<bool>(forgettingScore > 0.8 && utilityPreservation > 0.9);
        }
    }
}
