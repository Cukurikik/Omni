// OMNI Domain Layer - LlamaIndex Node Schema
namespace Omni.Domain.LlamaIndex {
    public enum NodeError { None, MissingContent }

    public class Result<T> {
        public T Value { get; }
        public NodeError Error { get; }
        public bool IsOk => Error == NodeError.None;

        public Result(T value) { Value = value; Error = NodeError.None; }
        public Result(NodeError error) { Error = error; }
    }

    public class NodeValidator {
        public Result<bool> ValidateTextNode(string content) {
            if (string.IsNullOrWhiteSpace(content)) {
                return new Result<bool>(NodeError.MissingContent);
            }
            return new Result<bool>(true);
        }
    }
}
