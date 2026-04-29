// OMNI Domain Layer - Kiln Synthetic Data
namespace Omni.Domain.Kiln {
    public enum DataGenError { None, InvalidTemperature }

    public class Result<T> {
        public T Value { get; }
        public DataGenError Error { get; }
        public bool IsOk => Error == DataGenError.None;

        public Result(T value) { Value = value; Error = DataGenError.None; }
        public Result(DataGenError error) { Error = error; }
    }

    public class SyntheticValidator {
        public Result<bool> ValidateGenerationTemp(double temp) {
            if (temp < 0.7 || temp > 1.5) { // Needs creativity but not gibberish
                return new Result<bool>(DataGenError.InvalidTemperature);
            }
            return new Result<bool>(true);
        }
    }
}
