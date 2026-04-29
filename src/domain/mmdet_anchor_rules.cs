// OMNI Domain Layer - MMDetection Anchor Rules
namespace Omni.Domain.MMDetection {
    public enum AnchorError { None, InvalidRatio }

    public class Result<T> {
        public T Value { get; }
        public AnchorError Error { get; }
        public bool IsOk => Error == AnchorError.None;

        public Result(T value) { Value = value; Error = AnchorError.None; }
        public Result(AnchorError error) { Error = error; }
    }

    public class AnchorValidator {
        public Result<bool> ValidateAspectRatio(double ratio) {
            if (ratio <= 0.0 || ratio > 10.0) {
                return new Result<bool>(AnchorError.InvalidRatio);
            }
            return new Result<bool>(true);
        }
    }
}
