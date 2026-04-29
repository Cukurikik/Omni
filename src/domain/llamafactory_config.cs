// OMNI Domain Layer - LlamaFactory Config
namespace Omni.Domain.LlamaFactory {
    public enum ConfigError { None, InvalidRank }

    public class Result<T> {
        public T Value { get; }
        public ConfigError Error { get; }
        public bool IsOk => Error == ConfigError.None;

        public Result(T value) { Value = value; Error = ConfigError.None; }
        public Result(ConfigError error) { Error = error; }
    }

    public class LoRAValidator {
        public Result<bool> ValidateRank(int r) {
            if (r <= 0 || r > 256) {
                return new Result<bool>(ConfigError.InvalidRank);
            }
            return new Result<bool>(true);
        }
    }
}
