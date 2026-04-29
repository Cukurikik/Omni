// OMNI Domain Layer - Llama.cpp Model Metadata
namespace Omni.Domain.LlamaCpp {
    public enum MetaError { None, InvalidArchitecture }

    public class Result<T> {
        public T Value { get; }
        public MetaError Error { get; }
        public bool IsOk => Error == MetaError.None;

        public Result(T value) { Value = value; Error = MetaError.None; }
        public Result(MetaError error) { Error = error; }
    }

    public class MetadataValidator {
        public Result<bool> ValidateArch(string arch) {
            if (string.IsNullOrEmpty(arch) || arch != "llama") {
                return new Result<bool>(MetaError.InvalidArchitecture);
            }
            return new Result<bool>(true);
        }
    }
}
