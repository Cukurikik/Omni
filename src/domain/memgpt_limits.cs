// OMNI Domain Layer - MemGPT Limits
namespace Omni.Domain.MemGPT {
    public enum LimitError { None, CoreMemoryExceeded }

    public class Result<T> {
        public T Value { get; }
        public LimitError Error { get; }
        public bool IsOk => Error == LimitError.None;

        public Result(T value) { Value = value; Error = LimitError.None; }
        public Result(LimitError error) { Error = error; }
    }

    public class MemoryPolicy {
        public Result<bool> ValidateCoreSize(int currentTokens, int maxTokens) {
            if (currentTokens > maxTokens) {
                return new Result<bool>(LimitError.CoreMemoryExceeded);
            }
            return new Result<bool>(true);
        }
    }
}
