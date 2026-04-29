// OMNI Domain Layer - Curator Data Quality Rules
namespace Omni.Domain.Curator {
    public enum QualityError { None, LowEntropy }

    public class Result<T> {
        public T Value { get; }
        public QualityError Error { get; }
        public bool IsOk => Error == QualityError.None;

        public Result(T value) { Value = value; Error = QualityError.None; }
        public Result(QualityError error) { Error = error; }
    }

    public class EntropyValidator {
        public Result<bool> ValidateTextEntropy(double entropyScore) {
            if (entropyScore < 1.5) {
                return new Result<bool>(QualityError.LowEntropy); // Data too repetitive
            }
            return new Result<bool>(true);
        }
    }
}
