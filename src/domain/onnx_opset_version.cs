// OMNI Domain Layer - ONNX Opset Version
namespace Omni.Domain.ONNX {
    public enum OpsetError { None, DeprecatedVersion }

    public class Result<T> {
        public T Value { get; }
        public OpsetError Error { get; }
        public bool IsOk => Error == OpsetError.None;

        public Result(T value) { Value = value; Error = OpsetError.None; }
        public Result(OpsetError error) { Error = error; }
    }

    public class Validator {
        public Result<bool> ValidateOpset(int version) {
            if (version < 13) {
                return new Result<bool>(OpsetError.DeprecatedVersion);
            }
            return new Result<bool>(true);
        }
    }
}
