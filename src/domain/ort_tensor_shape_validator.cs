// OMNI Domain Layer - ORT Tensor Shape Validator
namespace Omni.Domain.ORT {
    public enum ShapeError { None, DimensionMismatch }

    public class Result<T> {
        public T Value { get; }
        public ShapeError Error { get; }
        public bool IsOk => Error == ShapeError.None;

        public Result(T value) { Value = value; Error = ShapeError.None; }
        public Result(ShapeError error) { Error = error; }
    }

    public class TensorValidator {
        public Result<bool> ValidateInputShape(int[] expected, int[] actual) {
            if (expected.Length != actual.Length) {
                return new Result<bool>(ShapeError.DimensionMismatch);
            }
            return new Result<bool>(true);
        }
    }
}
