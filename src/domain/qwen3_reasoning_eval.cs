"// OMNI Domain Layer - Qwen3 Reasoning Eval\
namespace Omni.Domain.Qwen3 {\
    public enum EvalError { None, InvalidReasoningTrace }\
\
    public class Result<T> {\
        public T Value { get; }\
        public EvalError Error { get; }\
        public
<truncated 549 bytes>