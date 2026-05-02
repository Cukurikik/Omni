"// OMNI Domain Layer - Odyssey Embodied Rules\
namespace Omni.Domain.Odyssey {\
    public enum RuleError { None, InvalidAction }\
\
    public class Result<T> {\
        public T Value { get; }\
        public RuleError Error { get; }\
        public boo
<truncated 529 bytes>