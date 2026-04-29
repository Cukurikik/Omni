// OMNI Domain Layer - Axolotl Validation
namespace Omni.Domain.Axolotl {
    public enum ValidationError { None, InvalidEpochs }

    public class Result<T> {
        public T Value { get; }
        public ValidationError Error { get; }
        public bool IsOk => Error == ValidationError.None;

        public Result(T value) { Value = value; Error = ValidationError.None; }
        public Result(ValidationError error) { Error = error; }
    }

    public class TrainingValidator {
        public Result<bool> ValidateEpochs(int epochs) {
            if (epochs <= 0 || epochs > 100) {
                return new Result<bool>(ValidationError.InvalidEpochs);
            }
            return new Result<bool>(true);
        }
    }
}
