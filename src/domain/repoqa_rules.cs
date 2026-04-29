// OMNI Domain Layer - RepoQA Rules
namespace Omni.Domain.RepoQA {
    public enum RuleError { None, IndexTooLarge }

    public class Result<T> {
        public T Value { get; }
        public RuleError Error { get; }
        public bool IsOk => Error == RuleError.None;

        public Result(T value) { Value = value; Error = RuleError.None; }
        public Result(RuleError error) { Error = error; }
    }

    public class IndexValidator {
        public Result<bool> ValidateIndexSize(int totalFiles) {
            if (totalFiles > 10000) {
                return new Result<bool>(RuleError.IndexTooLarge);
            }
            return new Result<bool>(true);
        }
    }
}
