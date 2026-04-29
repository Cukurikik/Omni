// OMNI Domain Layer - TGI Router Rules
namespace Omni.Domain.TGI {
    public enum RouterError { None, PayloadTooLarge }

    public class Result<T> {
        public T Value { get; }
        public RouterError Error { get; }
        public bool IsOk => Error == RouterError.None;

        public Result(T value) { Value = value; Error = RouterError.None; }
        public Result(RouterError error) { Error = error; }
    }

    public class ValidationRouter {
        public Result<bool> ValidatePayloadSize(int inputTokens, int maxInputTokens) {
            if (inputTokens > maxInputTokens) {
                return new Result<bool>(RouterError.PayloadTooLarge);
            }
            return new Result<bool>(true);
        }
    }
}
