// OMNI Domain Layer - Neosync Anonymize Rules
namespace Omni.Domain.Neosync {
    public enum AnonymizeError { None, InvalidAlgorithm }

    public class Result<T> {
        public T Value { get; }
        public AnonymizeError Error { get; }
        public bool IsOk => Error == AnonymizeError.None;

        public Result(T value) { Value = value; Error = AnonymizeError.None; }
        public Result(AnonymizeError error) { Error = error; }
    }

    public class TransformerValidator {
        public Result<bool> ValidateTransformation(string algo) {
            if (algo != "mask" && algo != "faker" && algo != "hash") {
                return new Result<bool>(AnonymizeError.InvalidAlgorithm);
            }
            return new Result<bool>(true);
        }
    }
}
