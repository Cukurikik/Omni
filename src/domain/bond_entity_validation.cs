// OMNI Domain Layer - BOND Entity Validation
namespace Omni.Domain.BOND {
    public enum EntityError { None, InvalidTag }

    public class Result<T> {
        public T Value { get; }
        public EntityError Error { get; }
        public bool IsOk => Error == EntityError.None;

        public Result(T value) { Value = value; Error = EntityError.None; }
        public Result(EntityError error) { Error = error; }
    }

    public class BIOValidator {
        public Result<bool> ValidateBIOTag(string tag) {
            if (!tag.StartsWith("B-") && !tag.StartsWith("I-") && tag != "O") {
                return new Result<bool>(EntityError.InvalidTag);
            }
            return new Result<bool>(true);
        }
    }
}
