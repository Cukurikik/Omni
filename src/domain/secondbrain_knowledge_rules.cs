// OMNI Domain Layer - Second Brain Knowledge Rules
namespace Omni.Domain.SecondBrain {
    public enum KnowledgeError { None, CyclicalReference }

    public class Result<T> {
        public T Value { get; }
        public KnowledgeError Error { get; }
        public bool IsOk => Error == KnowledgeError.None;

        public Result(T value) { Value = value; Error = KnowledgeError.None; }
        public Result(KnowledgeError error) { Error = error; }
    }

    public class NoteGraphValidator {
        public Result<bool> ValidateAcyclic(string sourceId, string targetId) {
            if (sourceId == targetId) {
                return new Result<bool>(KnowledgeError.CyclicalReference);
            }
            return new Result<bool>(true);
        }
    }
}
