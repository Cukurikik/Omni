// OMNI Domain Layer - OpenCode Security Policy
namespace Omni.Domain.OpenCode {
    public enum SecurityError { None, ResourceLimitExceeded }

    public class Result<T> {
        public T Value { get; }
        public SecurityError Error { get; }
        public bool IsOk => Error == SecurityError.None;

        public Result(T value) { Value = value; Error = SecurityError.None; }
        public Result(SecurityError error) { Error = error; }
    }

    public class LimitsValidator {
        public Result<bool> ValidateExecutionTime(int expectedMs) {
            if (expectedMs > 5000) { // 5 second hard limit
                return new Result<bool>(SecurityError.ResourceLimitExceeded);
            }
            return new Result<bool>(true);
        }
    }
}
