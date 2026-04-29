// OMNI Domain Layer - DPO Policy
namespace Omni.Domain.DPO {
    public enum PolicyError { None, InvalidBeta }

    public class Result<T> {
        public T Value { get; }
        public PolicyError Error { get; }
        public bool IsOk => Error == PolicyError.None;

        public Result(T value) { Value = value; Error = PolicyError.None; }
        public Result(PolicyError error) { Error = error; }
    }

    public class AlignmentValidator {
        public Result<bool> ValidateHyperparameters(double beta) {
            if (beta <= 0.0 || beta > 1.0) {
                return new Result<bool>(PolicyError.InvalidBeta);
            }
            return new Result<bool>(true);
        }
    }
}
