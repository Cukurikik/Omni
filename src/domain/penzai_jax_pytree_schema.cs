// OMNI Domain Layer - Penzai JAX Pytree Schema
namespace Omni.Domain.Penzai {
    public enum TreeError { None, InvalidLeaf }

    public class Result<T> {
        public T Value { get; }
        public TreeError Error { get; }
        public bool IsOk => Error == TreeError.None;

        public Result(T value) { Value = value; Error = TreeError.None; }
        public Result(TreeError error) { Error = error; }
    }

    public class PytreeValidator {
        public Result<bool> ValidateLeafNode(object leaf) {
            if (leaf == null) {
                return new Result<bool>(TreeError.InvalidLeaf);
            }
            return new Result<bool>(true);
        }
    }
}
